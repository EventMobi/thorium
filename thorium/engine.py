class Engine(object):
    _authenticator_classes = None

    def __init__(self, request, response):
        self.request = request
        self.response = response
        self._authenticators = []
        if self._authenticator_classes:
            self._authenticators = [a(request) for a in self._authenticator_classes]

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
        raise NotImplementedError()

    def get_collection(self):
        raise NotImplementedError()

    def post_detail(self):
        raise NotImplementedError()

    def post_collection(self):
        raise NotImplementedError()

    def put_detail(self):
        raise NotImplementedError()

    def put_collection(self):
        raise NotImplementedError()

    def delete_detail(self):
        raise NotImplementedError()

    def delete_collection(self):
        raise NotImplementedError()

    def patch_detail(self):
        raise NotImplementedError()

    def patch_collection(self):
        raise NotImplementedError()

    def options(self):
        raise NotImplementedError()
