from .errors import InternalSeverError
from .serializer import JsonSerializer
from .response import ErrorResponse
import sys


class ExceptionHandler(object):

    def __init__(self, logger):
        self.logger = logger
        self.serializer = JsonSerializer()

    def handle_general_exception(self, url, method, e, request):
        """
        Logs an exception then returns an InternalServerError http response body
        """
        self.logger.error('Exception on {0} [{1}]'.format(url, method), exc_info=sys.exc_info())
        return self.handle_http_exception(InternalSeverError(), request)

    def handle_http_exception(self, http_error, request):
        """
        Builds a response body for a http exception.
        """
        error_response = ErrorResponse(http_error, request)
        serialized_response = self.serializer.serialize_response(error_response)
        return serialized_response





