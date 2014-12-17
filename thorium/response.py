from collections import OrderedDict
from operator import attrgetter
from . import errors

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
        raise NotImplementedError(
            'This method must be overridden by subclass.')


class DetailResponse(Response):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response_type = 'detail'
        self.resource = None

    def get_response_data(self):
        data = None
        if self.resource:
            data = OrderedDict(self.resource.sorted_items())
        return data


class CollectionResponse(Response):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response_type = 'collection'
        self.resources = []
        request = kwargs.get('request')
        self.sort = request.params.sort if hasattr(request.params,
                                                   'sort') else None
        self.offset = request.params.page if hasattr(request.params,
                                                   'offset') else None
        self.limit = request.params.per_page if hasattr(request.params,
                                                           'limit') else None

    def get_response_data(self):
        data = []
        if self.resources:
            self._sort()
            self._paginate()
            for res in self.resources:
                data.append(OrderedDict(res.sorted_items()))
        return data

    def _sort(self):
        if self.sort:
            reverse = self._check_and_strip_first_char()
            sort_by = self.sort.split(
                ',')  # split query parameters into a list
            try:
                self.resources.sort(key=attrgetter(*sort_by),
                                    reverse=reverse)
            except:
                raise errors.BadRequestError('Sort parameter doens\'t exist as a field')

    def _paginate(self):
        if self.offset and self.limit:
            end = self.offset + self.limit + 1
            self.resources = self.resources[self.offset:end]

    def _check_and_strip_first_char(self):
        reverse = True if self.sort.startswith('-') else False
        self.sort = self.sort.strip('+')
        self.sort = self.sort.strip('-')
        return reverse


class ErrorResponse(Response):
    def __init__(self, http_error, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response_type = 'error'
        self.status_code = http_error.status_code
        self.error = str(http_error)

    def get_response_data(self):
        return None