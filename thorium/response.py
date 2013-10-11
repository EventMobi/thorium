class Response(object):

    def __init__(self, request):
        self.headers = {}
        self.request = request
        self.status_code = self._set_status_code()

    def location_header(self, resource_id):
        ep = self.request.url
        if not ep.endswith('/'):
            ep += '/'
        ep += str(resource_id)
        self.headers['Location'] = ep

    def _set_status_code(self):
        if self.request.method == 'POST':
            return 201
        elif self.request.method == 'DELETE':
            return 204
        else:
            return 200


class DetailResponse(Response):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resource = None

    def set_resource_from_dict(self, data):
        if not self.resource:
            self.resource = self.request.resource_cls()
        self.resource.from_dict(data)
        return self.resource


class CollectionResponse(Response):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resources = []

    def add_resource_from_dict(self, data):
        res = self.request.resource_cls()
        res.from_dict(data)
        self.resources.append(res)
        return res