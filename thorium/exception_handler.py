import json
from .errors import InternalSeverError
import sys


class ExceptionHandler(object):

    def __init__(self, logger):
        self.logger = logger

    def handle_general_exception(self, request, e):
        """
        Logs an exception then returns an InternalServerError http response body
        """
        self.logger.error('Exception on {0} [{1}]'.format(request.url, request.method), exc_info=sys.exc_info())
        return self.handle_http_exception(InternalSeverError())

    def handle_http_exception(self, e):
        """
        Builds a response body for a http exception.
        """
        return json.dumps({'error': str(e), 'status': e.status_code})