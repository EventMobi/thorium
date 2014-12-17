from unittest import TestCase, mock
from thorium.response import Response, DetailResponse, CollectionResponse, \
    ErrorResponse
from thorium.errors import MethodNotAllowedError
from thorium import Resource, fields


class SimpleResource(Resource):
    id = fields.IntField()
    name = fields.CharField()


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
        self.assertEqual(self.response.meta, {})
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
        del self.request_mock.params.sort
        del self.request_mock.params.limit
        del self.request_mock.params.offset
        self.response = CollectionResponse(request=self.request_mock)

    def test_attributes(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.response.error, None)
        self.assertEqual(self.response.meta, {})
        self.assertEqual(self.response.response_type, 'collection')
        self.assertEqual(self.response.resources, [])

    def test_get_response_data_empty(self):
        data = self.response.get_response_data()
        self.assertEqual(data, [])

    def test_get_response_data(self):
        self.response.resources = [SimpleResource(id=1, name='a')]
        data = self.response.get_response_data()
        self.assertEqual(data, [{'id': 1, 'name': 'a'}])

    def test_get_response_data_sorted_by_id(self):
        self.response.resources = [SimpleResource(id=2, name='c'),
                                   SimpleResource(id=1, name='a'),
                                   SimpleResource(id=3, name='b')]
        self.response.sort = '+id'
        data = self.response.get_response_data()
        self.assertEqual(data[0], {'id': 1, 'name': 'a'})
        self.assertEqual(data[1], {'id': 2, 'name': 'c'})
        self.assertEqual(data[2], {'id': 3, 'name': 'b'})

    def test_get_response_data_sorted_by_name_and_id(self):
        self.response.resources = [SimpleResource(id=1, name='a'),
                                   SimpleResource(id=2, name='c'),
                                   SimpleResource(id=4, name='b'),
                                   SimpleResource(id=3, name='b')
        ]
        self.response.sort = '+name,id'
        data = self.response.get_response_data()
        self.assertEqual(data[0], {'id': 1, 'name': 'a'})
        self.assertEqual(data[1], {'id': 3, 'name': 'b'})
        self.assertEqual(data[2], {'id': 4, 'name': 'b'})
        self.assertEqual(data[3], {'id': 2, 'name': 'c'})

    def test_get_response_data_paginate(self):
        self.response.resources = [SimpleResource(id=1, name='a'),
                                   SimpleResource(id=2, name='c'),
                                   SimpleResource(id=3, name='b'),
                                   SimpleResource(id=4, name='d')]
        self.response.sort = '-name'
        self.response.limit = 2
        self.response.offset = 2
        data = self.response.get_response_data()
        self.assertEqual(data[0], {'id': 3, 'name': 'b'})
        self.assertEqual(data[1], {'id': 1, 'name': 'a'})


class TestErrorResponse(TestCase):
    def setUp(self):
        self.request_mock = mock.MagicMock()
        self.error = MethodNotAllowedError()
        self.response = ErrorResponse(http_error=self.error,
                                      request=self.request_mock)

    def test_attributes(self):
        self.assertEqual(self.response.status_code, 405)
        self.assertEqual(self.response.error, str(self.error))
        self.assertEqual(self.response.meta, {})
        self.assertEqual(self.response.response_type, 'error')

    def test_get_response_data_empty(self):
        data = self.response.get_response_data()
        self.assertEqual(data, None)