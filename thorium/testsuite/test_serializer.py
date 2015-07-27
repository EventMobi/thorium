# -*- coding: utf-8 -*-

import unittest
import json

from unittest import mock

from thorium.response import CollectionResponse, DetailResponse, ErrorResponse
from thorium.serializer import JsonSerializer
from thorium.errors import MethodNotAllowedError
from thorium import Resource, fields


class SimpleResource(Resource):
    id = fields.IntField()
    name = fields.CharField()


class TestJsonSerializer(unittest.TestCase):

    def setUp(self):
        self.serializer = JsonSerializer()
        self.data = {'id': 1, 'name': 'Jim'}
        self.request = mock.MagicMock()
        self.request.params = None

    def test_serialize_collection_response(self):
        collection_response = CollectionResponse(request=self.request)
        collection_response.resources = [SimpleResource(self.data)]
        serialized_data = self.serializer.serialize_response(collection_response)
        data = json.loads(serialized_data)
        expected_data = {
            "type": "collection",
            "error": None,
            "status": 200,
            "meta": {
                'pagination': {
                    'paginated': False,
                    'paginated': False,
                    'limit': None,
                    'offset': None,
                    'record_count': 0,
                }
            },
            "data": [self.data]
        }
        self.assertDictEqual(data, expected_data)

    def test_serialize_empty_collection_response(self):
        collection_response = CollectionResponse(request=self.request)
        serialized_data = self.serializer.serialize_response(collection_response)
        data = json.loads(serialized_data)
        expected_data = {
            "type": "collection",
            "error": None,
            "status": 200,
            "meta": {
                'pagination': {
                    'paginated': False,
                    'paginated': False,
                    'limit': None,
                    'offset': None,
                    'record_count': 0,
                }
            },
            "data": []
        }
        self.assertEqual(data, expected_data)

    def test_serialize_detail_response(self):
        detail_response = DetailResponse(self.request)
        detail_response.resource = SimpleResource(self.data)
        serialized_data = self.serializer.serialize_response(detail_response)
        data = json.loads(serialized_data)
        expected_data = {
            "type": "detail",
            "error": None,
            "status": 200,
            "meta": {
                'pagination': None,
            },
            "data": self.data
        }
        self.assertEqual(data, expected_data)

    def test_serialize_empty_detail_response(self):
        detail_response = DetailResponse(self.request)
        serialized_data = self.serializer.serialize_response(detail_response)
        data = json.loads(serialized_data)
        expected_data = {
            "type": "detail",
            "error": None,
            "status": 200,
            "meta": {
                'pagination': None,
            },
            "data": None
        }
        self.assertEqual(data, expected_data)

    def test_serialize_error_response(self):
        http_error = MethodNotAllowedError()
        error_response = ErrorResponse(http_error, self.request)
        serialized_data = self.serializer.serialize_response(error_response)
        data = json.loads(serialized_data)
        expected_data = {
            "type": "error",
            "error": str(http_error),
            "status": http_error.status_code,
            "meta": {
                'pagination': None,
            },
            "data": None
        }
        self.assertEqual(data, expected_data)
