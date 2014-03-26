class Response(object):

    def __init__(self, request):
        self.meta = {}
        self.headers = {}
        self.request = request
        self.error = None
        self.response_type = None
        self.status_code = self._set_status_code()

    def location_header(self, resource_id):
        ep = self.request.url
        if not ep.endswith('/'):
            ep += '/'
        ep += str(resource_id)
        self.headers['Location'] = ep

    def _set_status_code(self):
        if not self.request:  # Hacky
            return 500

        if self.request.method == 'POST':
            return 201
        elif self.request.method == 'DELETE':
            return 204
        else:
            return 200

    def get_response_data(self):
        raise NotImplementedError('This method must be overridden by subclass.')


class DetailResponse(Response):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response_type = 'detail'
        self.resource = None

    def get_response_data(self):
        data = None
        if self.resource:
            data = {n: v.get() for n, v in self.resource.all_fields()}
        return data


class CollectionResponse(Response):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response_type = 'collection'
        self.resources = []

    def get_response_data(self):
        data = []
        if self.resources:
            for res in self.resources:
                data.append({n: v.get() for n, v in res.all_fields()})
        return data


class ErrorResponse(Response):

    def __init__(self, http_error, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response_type = 'error'
        self.status_code = http_error.status_code
        self.error = str(http_error)

    def get_response_data(self):
        return None