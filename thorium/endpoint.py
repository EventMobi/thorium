from . import errors


class Endpoint(object):
    """
    Responsible for the implementation of a single :class:`Resource`,
    The methods provide hooks which will be called into by the dispatcher
    during a request.

    :param request: A :class:`Request` object.
    :param response: A :class:`Response` object.
    """

    _authenticator_classes = None
    Resource = None

    def __init__(self, request, response):
        self.request = request
        self.response = response
        self._authenticators = []
        if self._authenticator_classes:
            self._authenticators = [a(self) for a in self._authenticator_classes]

    def authenticate(self, method):
        if self._authenticators:
            for auth in self._authenticators:
                auth.check_auth(method)

    def pre_request(self):
        pass

    def pre_request_detail(self):
        pass

    def pre_request_collection(self):
        pass

    def post_request(self):
        pass

    def get_detail(self):
        raise errors.MethodNotImplementedError()

    def get_collection(self):
        raise errors.MethodNotImplementedError()

    def post_detail(self):
        raise errors.MethodNotImplementedError()

    def post_collection(self):
        raise errors.MethodNotImplementedError()

    def put_detail(self):
        raise errors.MethodNotImplementedError()

    def put_collection(self):
        raise errors.MethodNotImplementedError()

    def delete_detail(self):
        raise errors.MethodNotImplementedError()

    def delete_collection(self):
        raise errors.MethodNotImplementedError()

    def patch_detail(self):
        raise errors.MethodNotImplementedError()

    def patch_collection(self):
        raise errors.MethodNotImplementedError()

    def options(self):
        raise errors.MethodNotImplementedError()


