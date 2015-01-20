# -*- coding: utf-8 -*-

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
        self.offset = getattr(self.request.params, 'offset', None)
        self.limit = getattr(self.request.params, 'limit', None)

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
            sort_by = self.sort.split(',')
            for field in sort_by:
                if not hasattr(self.resources[0], field):
                    raise errors.BadRequestError(
                        'Cannot sort by field `{}`. It does not exist in the '
                        'resource.'.format(field)
                    )
            self.resources.sort(key=attrgetter(*sort_by), reverse=reverse)

    def _paginate(self):
        if self.offset is not None and self.limit is not None:
            self._validate_offset_and_limit()
            if self.offset < 0:
                raise errors.BadRequestError('Offset cannot be negative.')
            if self.limit < 1:
                raise errors.BadRequestError('Limit must be greater than 1.')
            self.meta['offset'] = self.offset
            self.meta['limit'] = self.limit
            start = self.offset
            end = self.offset + self.limit
            self.resources = self.resources[start:end]

    def _check_and_strip_first_char(self):
        self.meta['sort'] = self.sort
        reverse = self.sort.startswith('-')
        self.sort = self.sort.lstrip('+-')
        return reverse

    def _validate_offset_and_limit(self):
        try:
            if isinstance(self.offset, bool) or isinstance(self.limit, bool):
                raise TypeError
            self.offset = int(self.offset)
            self.limit = int(self.limit)
        except (ValueError, TypeError):
            raise errors.BadRequestError(
                'Both `offset` and `limit` must be valid numbers. Could not '
                'cast offset of `{0}` or limit of `{1}`.'
                .format(self.offset, self.limit)
            )


class ErrorResponse(Response):

    def __init__(self, http_error, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response_type = 'error'
        self.status_code = http_error.status_code
        self.error = str(http_error)

    def get_response_data(self):
        return None
