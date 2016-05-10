import json
import traceback
from flask import Response as FlaskResponse


class ValidationError(Exception):
    pass


class HttpErrorBase(Exception):
    status_code = None
    default_message = None

    def __init__(self, message=None, headers=None, code=None):
        self.headers = headers if headers else {}
        self.code = code
        self.params = getattr(message, 'params', None)
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


class ConflictError(HttpErrorBase):
    status_code = 409
    default_message = 'Request could not be processed because of a conflict.'


class InternalSeverError(HttpErrorBase):
    status_code = 500
    default_message = 'The server encountered an internal error or misconfiguration and was unable to complete your ' \
                      'request. Please try again later or contact the server administrator.'


class MethodNotImplementedError(HttpErrorBase):
    status_code = 500
    default_message = 'The attempted method was not found at this endpoint.'
