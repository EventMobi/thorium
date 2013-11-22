import json
import traceback
from flask import Response as FlaskResponse


class ValidationError(Exception):
    pass


class HttpErrorBase(Exception):
    status_code = None
    default_message = None

    def __init__(self, message=None, headers={}):
        self.headers = headers
        super().__init__(message or self.default_message)


class BadRequestError(HttpErrorBase):
    status_code = 400
    default_message = 'Badly formed request.'


class UnauthorizedError(HttpErrorBase):
    status_code = 401
    default_message = 'Attempted action requires authentication.'


class ForbiddenError(HttpErrorBase):
    status_code = 403
    default_message = 'Supplied credentials not authorized for attempted action.'


class ResourceNotFoundError(HttpErrorBase):
    status_code = 404
    default_message = 'Expected resource was not found.'


class MethodNotAllowedError(HttpErrorBase):
    status_code = 405
    default_message = 'Attempted method not allowed on this resource.'


class InternalSeverError(HttpErrorBase):
    status_code = 500
    default_message = 'The server encountered an internal error or misconfiguration and was unable to complete your ' \
                      'request. Please try again later or contact the server administrator.'


class MethodNotImplementedError(HttpErrorBase):
    status_code = 500
    default_message = 'The attempted method was not found at this endpoint.'


class ExceptionHandler(object):

    @staticmethod
    def handle_general_exception(e):
        return ExceptionHandler.handle_http_exception(InternalSeverError())

    @staticmethod
    def handle_http_exception(e):
        error = json.dumps({'error': str(e), 'status': e.status_code})
        return FlaskResponse(response=error, status=e.status_code, headers=e.headers, content_type='application/json')