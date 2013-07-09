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
    default_message = 'Expected resource was not found.'


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