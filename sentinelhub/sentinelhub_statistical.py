"""
Implementation of Sentinel Hub Statistical API interface
"""
from .constants import MimeType
from .download.sentinelhub_statistical_client import SentinelHubStatisticalDownloadClient
from .sentinelhub_base_api import SentinelHubBaseApiRequest
from .sh_utils import _update_other_args
from .time_utils import parse_time_interval, serialize_time


class SentinelHubStatistical(SentinelHubBaseApiRequest):
    """ Sentinel Hub Statistical API interface

    For more information check
    `Statistical API documentation <https://docs.sentinel-hub.com/api/latest/api/statistical/>`__.
    """
    _SERVICE_ENDPOINT = 'statistics'

    def __init__(self, aggregation, input_data, bbox=None, geometry=None, calculations=None, **kwargs):
        """
        For details of certain parameters check the
        `Statistical API reference <https://docs.sentinel-hub.com/api/latest/reference/#tag/statistical>`_.

        :param aggregation: Aggregation part of the payload, which can be generated with `aggregation` method
        :type aggregation: dict
        :param input_data: A list of input dictionary objects as described in the API reference. It can be generated
            with `input_data` method
        :type input_data: List[dict or InputDataDict]
        :param bbox: A bounding box of the request
        :type bbox: sentinelhub.BBox or None
        :param geometry: A geometry of the request
        :type geometry: sentinelhub.Geometry or None
        :param calculations: Calculations part of the payload.
        :param calculations: dict
        :param data_folder: Location of the directory where the downloaded data could be saved.
        :type data_folder: str
        :param config: A custom instance of config class to override parameters from the saved configuration.
        :type config: SHConfig or None
        """
        self.mime_type = MimeType.JSON

        self.payload = self.body(
            request_bounds=self.bounds(bbox=bbox, geometry=geometry),
            request_data=input_data,
            aggregation=aggregation,
            calculations=calculations
        )

        super().__init__(SentinelHubStatisticalDownloadClient, **kwargs)

    @staticmethod
    def body(request_bounds, request_data, aggregation, calculations, other_args=None):
        """ Generate the Process API request body

        :param request_bounds: A dictionary as generated by `bounds` helper method.
        :type request_bounds: dict
        :param request_data: A list of dictionaries as generated by `input_data` helper method.
        :type request_data: List[dict]
        :param aggregation: A dictionary as generated by `aggregation` helper method.
        :type aggregation: dict
        :param calculations: A dictionary defining calculations part of the payload
        :type calculations: dict
        :param other_args: Additional dictionary of arguments. If provided, the resulting dictionary will get updated
            by it.
        :param other_args: dict
        :returns: Request payload dictionary
        :rtype: dict
        """
        # Some parts of the payload have to be defined:
        for input_data_payload in request_data:
            if 'dataFilter' not in input_data_payload:
                input_data_payload['dataFilter'] = {}

        if calculations is None:
            calculations = {
                'default': {}
            }

        request_body = {
            'input': {
                'bounds': request_bounds,
                'data': request_data
            },
            'aggregation': aggregation,
            'calculations': calculations
        }

        if other_args:
            _update_other_args(request_body, other_args)

        return request_body

    @staticmethod
    def aggregation(evalscript, time_interval, aggregation_interval, size=None, resolution=None, other_args=None):
        """ Generate the `aggregation` part of the Statistical API request body

        :param evalscript: An `evalscript <https://docs.sentinel-hub.com/api/latest/#/Evalscript/>`_.
        :type evalscript: str
        :param time_interval: An interval with start and end date of the form YYYY-MM-DDThh:mm:ss or YYYY-MM-DD or
            a datetime object
        :type time_interval: (str, str) or (datetime, datetime)
        :param aggregation_interval: How data from given time interval is aggregated together
        :type aggregation_interval: str
        :param size: A width and height of an image from which data will be aggregated
        :type size: (int, int) or None
        :param resolution: A resolution in x and y dimensions of an image from which data will be aggregated.
            Resolution has to be defined in the same units as request bbox or geometry
        :type resolution: (float, float) or (int, int) or None
        :param other_args: Additional dictionary of arguments. If provided, the resulting dictionary will get updated
            by it.
        :param other_args: dict
        :returns: Aggregation payload dictionary
        :rtype: dict
        """
        start_time, end_time = serialize_time(parse_time_interval(time_interval, allow_undefined=True), use_tz=True)

        payload = {
            'evalscript': evalscript,
            'timeRange': {
                'from': start_time,
                'to': end_time
            },
            'aggregationInterval': {
                'of': aggregation_interval
            }
        }

        if size:
            payload['width'], payload['height'] = size
        if resolution:
            payload['resx'], payload['resy'] = resolution

        if other_args:
            _update_other_args(payload, other_args)

        return payload
