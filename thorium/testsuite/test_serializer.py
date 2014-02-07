import unittest
import json
from unittest import mock
from thorium.serializer import SerializerBase, JsonSerializer, CollectionResponse, DetailResponse
from thorium import Resource, fields


class TestSerializerBase(unittest.TestCase):

    def setUp(self):
        self.serializer_base = SerializerBase()

    def test_serialize_collection_response(self):
        response = mock.MagicMock(spec=CollectionResponse)
        response.resources = [mock.MagicMock()]
        response.meta = {}
        self.assertRaises(NotImplementedError, self.serializer_base.serialize_response, response)

    def test_serialize_detail_response(self):
        response = mock.MagicMock(spec=DetailResponse)
        response.resource = mock.MagicMock()
        self.assertRaises(NotImplementedError, self.serializer_base.serialize_response, response)


class SimpleResource(Resource):
    id = fields.IntField()
    name = fields.CharField()


class TestJsonSerializer(unittest.TestCase):

    def setUp(self):
        self.serializer = JsonSerializer()
        self.data = {'id': 1, 'name': 'Jim'}

    def test_serialize_collection_response(self):
        response = mock.MagicMock(spec=CollectionResponse)
        response.resources = [SimpleResource(self.data)]
        response.meta = {}
        serialized_data = self.serializer.serialize_response(response)
        self.assertEqual(serialized_data, json.dumps({'items': [self.data], '_meta': {}}))

    def test_serialize_empty_collection_response(self):
        response = mock.MagicMock(spec=CollectionResponse)
        response.resources = []
        response.meta = {}
        serialized_data = self.serializer.serialize_response(response)
        self.assertEqual(serialized_data, json.dumps({'items': [], '_meta': {}}))

    def test_serialize_detail_response(self):
        response = mock.MagicMock(spec=DetailResponse)
        response.resource = SimpleResource(self.data)
        serialized_data = self.serializer.serialize_response(response)
        self.assertEqual(serialized_data, json.dumps(self.data))

    def test_serialize_empty_detail_response(self):
        response = mock.MagicMock(spec=DetailResponse)
        response.resource = None
        serialized_data = self.serializer.serialize_response(response)
        self.assertEqual(serialized_data, json.dumps({}))