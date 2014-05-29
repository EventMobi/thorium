import sys,traceback,json,datetime,socket
from .errors import InternalSeverError
from .serializer import JsonSerializer
from .response import ErrorResponse

class ExceptionHandler(object):

    def __init__(self, logger):
        self.logger = logger
        self.serializer = JsonSerializer()

    def handle_general_exception(self, url, method, e, request):
        """
        Logs an exception then returns an InternalServerError http response body exc_info=1
        """
        message = e.args[0]
        stack_trace = ''.join(traceback.format_tb(sys.exc_info()[2]))
        exception_type = str(type(e))
        time_stamp = datetime.datetime.now().isoformat()
        host_name = socket.gethostname()

        json_envelope = {
            "type": "exception",
            "time_stamp": time_stamp,
            "host_name": host_name,
            "url": url,
            "method": method,
            "message": message,
            "stack_trace": stack_trace,
            "exception_type":  exception_type,
            "comment": "this is a comment"
        }

        self.logger.error(json.dumps(json_envelope), exc_info=0)

        return self.handle_http_exception(InternalSeverError(), request)

    def handle_http_exception(self, http_error, request):
        """
        Builds a response body for a http exception.
        """
        error_response = ErrorResponse(http_error, request)
        serialized_response = self.serializer.serialize_response(error_response)
        return serialized_response