# -*- coding: utf-8 -*-

from unittest import TestCase, mock

from thorium.response import (Response, DetailResponse, CollectionResponse,
                              ErrorResponse)
from thorium.errors import MethodNotAllowedError, BadRequestError
from thorium import Resource, fields


class SimpleResource(Resource):
    id = fields.IntField()
    name = fields.CharField()


class ComplexResource(Resource):
    id = fields.IntField(notnull=True)
    name = fields.CharField(default='noname')
    items = fields.ListField(item_type=fields.IntField())
    hash_map = fields.DictField(notnull=True)
    unique = fields.SetField()


class TestResponse(TestCase):

    def setUp(self):
        self.request_mock = mock.MagicMock()
        self.response = Response(request=self.request_mock)

    def test_location_header(self):
        self.request_mock.url = 'http://testurl/api'
        self.response.location_header(10)
        self.assertEqual(self.response.headers['Location'],
                         'http://testurl/api/10')

    def test_get_response_data_raises_error(self):
        self.assertRaises(NotImplementedError, self.response.get_response_data)


class TestDetailResponse(TestCase):

    def setUp(self):
        self.request_mock = mock.MagicMock()
        self.response = DetailResponse(request=self.request_mock)

    def test_attributes(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.response.error, None)
        self.assertEqual(self.response.meta, {'pagination': None})
        self.assertEqual(self.response.response_type, 'detail')
        self.assertEqual(self.response.resource, None)

    def test_get_response_data_empty(self):
        data = self.response.get_response_data()
        self.assertEqual(data, None)

    def test_get_response_data(self):
        self.response.resource = SimpleResource(id=1, name='a')
        data = self.response.get_response_data()
        self.assertEqual(data, {'id': 1, 'name': 'a'})


class TestCollectionResponse(TestCase):

    def setUp(self):
        self.request_mock = mock.MagicMock()
        self.request_mock.params.sort = None
        self.request_mock.params.offset = None
        self.request_mock.params.limit = None
        self.response = CollectionResponse(request=self.request_mock)
        self.test_data = [
            SimpleResource(id=1, name='a'),
            SimpleResource(id=2, name='c'),
            SimpleResource(id=4, name='b'),
            SimpleResource(id=3, name='d'),
            SimpleResource(id=5, name='d'),
        ]
        self.test_data_none = [
            SimpleResource(id=1, name='a'),
            SimpleResource(id=1, name=None),
            SimpleResource(id=3, name='b'),
        ]
        self.test_data_complex = [
            ComplexResource(id=3, items=[], hash_map={'one': 1}, unique=set()),
            ComplexResource(id=1, items=[1], hash_map={}, unique=None),
            ComplexResource(id=2, items=None, hash_map={}, unique={1, 2})
        ]

    def test_attributes(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.response.error, None)
        self.assertEqual(
            self.response.meta,
            {
                'pagination': {
                    'paginated': False,
                    'limit': None,
                    'offset': None,
                    'record_count': 0,
                }
            }
        )
        self.assertEqual(self.response.response_type, 'collection')
        self.assertEqual(self.response.resources, [])

    def test_get_response_data_empty(self):
        data = self.response.get_response_data()
        self.assertEqual(data, [])

    def test_get_response_data(self):
        self.response.resources = [SimpleResource(id=1, name='a')]
        data = self.response.get_response_data()
        self.assertEqual(data, [{'id': 1, 'name': 'a'}])

    def test_get_response_data_sort_ascending(self):
        self.response.resources = self.test_data
        self.response.sort = '+id'
        data = self.response.get_response_data()
        self.assertEqual(len(data), len(self.test_data))
        self.assertEqual(data[0], {'id': 1, 'name': 'a'})
        self.assertEqual(data[1], {'id': 2, 'name': 'c'})
        self.assertEqual(data[2], {'id': 3, 'name': 'd'})
        self.assertEqual(data[3], {'id': 4, 'name': 'b'})
        self.assertEqual(data[4], {'id': 5, 'name': 'd'})

    def test_get_response_data_sort_ascending_multiple(self):
        self.response.resources = self.test_data
        self.response.sort = 'name,id'
        data = self.response.get_response_data()
        self.assertEqual(len(data), len(self.test_data))
        self.assertEqual(data[0], {'id': 1, 'name': 'a'})
        self.assertEqual(data[1], {'id': 4, 'name': 'b'})
        self.assertEqual(data[2], {'id': 2, 'name': 'c'})
        self.assertEqual(data[3], {'id': 3, 'name': 'd'})
        self.assertEqual(data[4], {'id': 5, 'name': 'd'})

    def test_get_response_data_sort_descending(self):
        self.response.resources = self.test_data
        self.response.sort = '-id'
        data = self.response.get_response_data()
        self.assertEqual(len(data), len(self.test_data))
        self.assertEqual(data[0], {'id': 5, 'name': 'd'})
        self.assertEqual(data[1], {'id': 4, 'name': 'b'})
        self.assertEqual(data[2], {'id': 3, 'name': 'd'})
        self.assertEqual(data[3], {'id': 2, 'name': 'c'})
        self.assertEqual(data[4], {'id': 1, 'name': 'a'})

    def test_get_response_data_sort_descending_multiple(self):
        self.response.resources = self.test_data
        self.response.sort = '-name,-id'
        data = self.response.get_response_data()
        self.assertEqual(len(data), len(self.test_data))
        self.assertEqual(data[0], {'id': 5, 'name': 'd'})
        self.assertEqual(data[1], {'id': 3, 'name': 'd'})
        self.assertEqual(data[2], {'id': 2, 'name': 'c'})
        self.assertEqual(data[3], {'id': 4, 'name': 'b'})
        self.assertEqual(data[4], {'id': 1, 'name': 'a'})

    def test_get_response_data_sort_mixed(self):
        self.response.resources = self.test_data
        self.response.sort = '-name,+id'
        data = self.response.get_response_data()
        self.assertEqual(len(data), len(self.test_data))
        self.assertEqual(data[0], {'id': 3, 'name': 'd'})
        self.assertEqual(data[1], {'id': 5, 'name': 'd'})
        self.assertEqual(data[2], {'id': 2, 'name': 'c'})
        self.assertEqual(data[3], {'id': 4, 'name': 'b'})
        self.assertEqual(data[4], {'id': 1, 'name': 'a'})

    def test_get_response_data_sort_with_none(self):
        self.response.resources = self.test_data_none
        self.response.sort = 'name,-id'
        data = self.response.get_response_data()
        self.assertEqual(len(data), len(self.test_data_none))
        self.assertEqual(data[0], {'id': 1, 'name': None})
        self.assertEqual(data[1], {'id': 1, 'name': 'a'})
        self.assertEqual(data[2], {'id': 3, 'name': 'b'})

    def test_get_response_data_sort_invalid(self):
        self.response.resources = self.test_data
        self.response.sort = '+NotAField'
        self.assertRaises(BadRequestError, self.response.get_response_data)

        self.response.resources = self.test_data_complex
        self.response.sort = '-items'
        self.assertRaises(BadRequestError, self.response.get_response_data)
        self.response.sort = 'hash_map'
        self.assertRaises(BadRequestError, self.response.get_response_data)
        self.response.sort = 'unique'
        self.assertRaises(BadRequestError, self.response.get_response_data)

    def test_get_response_data_paginate(self):
        self.response.resources = self.test_data
        self.response.meta['pagination']['offset'] = 1
        self.response.meta['pagination']['limit'] = 1
        data = self.response.get_response_data()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0], {'id': 2, 'name': 'c'})

    def test_get_response_data_paginate_cast(self):
        self.response.resources = self.test_data
        self.response.sort = 'id'
        self.response.meta['pagination']['offset'] = '2'
        self.response.meta['pagination']['limit'] = '2'
        data = self.response.get_response_data()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0], {'id': 3, 'name': 'd'})
        self.assertEqual(data[1], {'id': 4, 'name': 'b'})

    def test_get_response_data_paginate_with_sort(self):
        self.response.resources = self.test_data
        self.response.sort = '-name'
        self.response.meta['pagination']['limit'] = 2
        self.response.meta['pagination']['offset'] = 2
        data = self.response.get_response_data()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0], {'id': 2, 'name': 'c'})
        self.assertEqual(data[1], {'id': 4, 'name': 'b'})

    def test_get_response_data_pagination_out_of_bounds(self):
        self.response.resources = self.test_data
        self.response.meta['pagination']['offset'] = 5
        self.response.meta['pagination']['limit'] = 10
        data = self.response.get_response_data()
        self.assertEqual(data, [])

    def test_get_response_data_invalid_offset(self):
        self.response.resources = self.test_data
        self.response.meta['pagination']['offset'] = -1
        self.response.meta['pagination']['limit'] = 10
        self.assertRaises(BadRequestError, self.response.get_response_data)

        self.response.offset = ''
        self.assertRaises(BadRequestError, self.response.get_response_data)

        self.response.offset = True
        self.assertRaises(BadRequestError, self.response.get_response_data)

    def test_get_response_data_invalid_limit(self):
        self.response.resources = self.test_data
        self.response.meta['pagination']['offset'] = 0
        self.response.meta['pagination']['limit'] = 0
        self.assertRaises(BadRequestError, self.response.get_response_data)

        self.response.limit = -1
        self.assertRaises(BadRequestError, self.response.get_response_data)

        self.response.limit = 'infinity'
        self.assertRaises(BadRequestError, self.response.get_response_data)

        self.response.limit = False
        self.assertRaises(BadRequestError, self.response.get_response_data)


class TestErrorResponse(TestCase):

    def setUp(self):
        self.request_mock = mock.MagicMock()
        self.error = MethodNotAllowedError()
        self.response = ErrorResponse(http_error=self.error,
                                      request=self.request_mock)

    def test_attributes(self):
        self.assertEqual(self.response.status_code, 405)
        self.assertEqual(self.response.error, str(self.error))
        self.assertEqual(self.response.meta, {'pagination': None})
        self.assertEqual(self.response.response_type, 'error')

    def test_get_response_data_empty(self):
        data = self.response.get_response_data()
        self.assertEqual(data, None)
