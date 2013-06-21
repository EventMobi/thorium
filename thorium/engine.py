class Engine(object):

    def __init__(self, request):
        self.request = request

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

