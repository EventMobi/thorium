# -*- coding: utf-8 -*-

from collections import OrderedDict
from operator import attrgetter

from . import errors


class Response(object):

    def __init__(self, request):
        self.meta = {
            'pagination': None,
        }
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
            'This method must be overridden by subclass.'
        )


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
        self.sort = getattr(self.request.params, 'sort', None)
        self.meta['pagination'] = {
            'paginated': False,
            'limit': getattr(self.request.params, 'limit', None),
            'offset': getattr(self.request.params, 'offset', None),
            'record_count': 0,
        }

    def get_response_data(self):
        data = []
        if self.resources:
            self._sort()
            self._paginate()
            for res in self.resources:
                fields = dict(res.all_fields())
                field_data = OrderedDict()
                for key, item in res.sorted_items():
                    if not fields[key].detail:
                        field_data[key] = item
                data.append(field_data)
        return data

    def _sort(self):
        if self.meta['pagination']['paginated']:
            return
        if self.sort:
            self.meta['sort'] = self.sort
            sort_by = self.sort.split(',')
            for field in reversed(sort_by):
                field, reverse = self._check_and_strip_first_char(field)
                self._validate_sort_field(field)
                not_sortable, sortable, = [], []
                for resource in self.resources:
                    if getattr(resource, field) is None:
                        not_sortable.append(resource)
                    else:
                        sortable.append(resource)
                sortable.sort(key=attrgetter(field), reverse=reverse)
                if reverse:
                    self.resources = sortable + not_sortable
                else:
                    self.resources = not_sortable + sortable

    def _paginate(self):
        if self.meta['pagination']['paginated']:
            return
        if  (self.meta['pagination']['offset'] is None or
             self.meta['pagination']['limit'] is None):
            return
        self._validate_offset_and_limit()
        if self.meta['pagination']['offset'] < 0:
            raise errors.BadRequestError('Offset cannot be negative.')
        if self.meta['pagination']['limit'] < 1:
            raise errors.BadRequestError('Limit must be greater than 1.')
        self.meta['offset'] = self.meta['pagination']['offset']
        self.meta['limit'] = self.meta['pagination']['limit']
        start = self.meta['offset']
        end = self.meta['pagination']['offset'] + self.meta['pagination']['limit']
        self.resources = self.resources[start:end]
        self.meta['pagination']['record_count'] = len(self.resources)
        self.meta['pagination']['next_page'] = start + len(self.resources)

    def _check_and_strip_first_char(self, field):
        reverse = field.startswith('-')
        field = field.lstrip('+-')
        return field, reverse

    def _validate_sort_field(self, field):
        if not hasattr(self.resources[0], field):
            raise errors.BadRequestError(
                'Cannot sort by field `{}`. It does not exist in the resource.'
                .format(field)
            )
        elif (isinstance(getattr(self.resources[0], field), dict) or
              isinstance(getattr(self.resources[0], field), list) or
              isinstance(getattr(self.resources[0], field), set)):
            raise errors.BadRequestError(
                'Cannot sort by field `{}`. Field type is not sortable.'
                .format(field)
            )

    def _validate_offset_and_limit(self):
        try:
            pagin = self.meta['pagination']
            if (isinstance(pagin['offset'], bool) or
                    isinstance(pagin['limit'], bool)):
                raise TypeError

            if pagin['offset'] is None and pagin['limit'] is None:
                return
            pagin['offset'] = int(pagin['offset'])
            pagin['limit'] = int(pagin['limit'])


        except (ValueError, TypeError):
            raise errors.BadRequestError(
                'Both `offset` and `limit` must be valid numbers. Could not '
                'cast offset of `{0}` or limit of `{1}`.'
                .format(self.meta['pagination']['offset'],
                        self.meta['pagination']['limit'])
            )


class ErrorResponse(Response):

    def __init__(self, http_error, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response_type = 'error'
        self.status_code = http_error.status_code
        self.error = str(http_error)
        self.code = getattr(http_error, 'code', None)
        self.params = getattr(http_error, 'params', None)

    def get_response_data(self):
        return None
