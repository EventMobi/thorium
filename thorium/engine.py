class Engine(object):
    _authenticator_classes = None

    def __init__(self, request):
        self.request = request
        if self._authenticator_classes:
            self._authenticators = [a(request) for a in self._authenticator_classes]

    def pre_request(self):
        pass

    def post_request(self):
        pass

    def get(self):
        raise NotImplementedError()

    def post(self):
        raise NotImplementedError()

    def put(self):
        raise NotImplementedError()

    def delete(self):
        raise NotImplementedError()

    def patch(self):
        raise NotImplementedError()

    def options(self):
        raise NotImplementedError()

    def authenticate(self, method):
        if self._authenticators:
            for auth in self._authenticators:
                auth.check_auth(method)