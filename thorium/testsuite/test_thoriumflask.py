from flask import Flask
import unittest
from unittest import mock
from thorium import ThoriumFlask, RouteManager, Resource, fields, Engine
import json
import datetime
import calendar


class PersonEngine(Engine):

    def pre_request(self):
        self.ds = DataStore()

    def get_detail(self):
        person = self.request.resource_cls()
        self.ds.populate_person(person)
        self.response.resource = person

    def get_collection(self):
        person = self.request.resource_cls()
        self.ds.populate_person(person)
        self.response.resources.append(person)


class PersonResource(Resource):
    id = fields.IntField(default=None)
    name = fields.CharField()
    birth_date = fields.DateTimeField()
    admin = fields.BoolField()

    class Params:
        email = fields.CharParam(default=None, max_length=200)
        q = fields.CharParam(default=None)
        ids = fields.CharParam()
        admin = fields.BoolParam()
        birth_date = fields.DateTimeParam()

    class Meta:
        collection_endpoint = '/api/event/<int:event_id>/people'
        collection_methods = {'get', 'post'}
        detail_endpoint = '/api/event/<int:event_id>/people/<int:id>'
        detail_methods = {'get', 'put', 'patch'}
        engine = PersonEngine


class DataStore(object):

    def populate_person(self, person):
        person.id = 42
        person.name = 'Timmy'
        person.birth_date = datetime.datetime(1974, 3, 13)
        person.admin = True


class TestThoriumFlask(unittest.TestCase):

    def setUp(self):
        route_manager = RouteManager()
        route_manager.register_resource(PersonResource)
        self.flask_app = Flask(__name__)
        ThoriumFlask(
            settings={},
            route_manager=route_manager,
            flask_app=self.flask_app
        )

    def test_simple_detail_get(self):
        rv = self.flask_app.test_client().open('/api/event/1/people/1', method='GET')
        self.assertEqual(rv.status_code, 200)
        data = json.loads(rv.data.decode())
        self.assertEqual(data['name'], 'Timmy')
        self.assertEqual(data['admin'], True)
        self.assertEqual(data['id'], 42)

    def test_simple_list_get(self):
        rv = self.flask_app.test_client().open('/api/event/1/people', method='GET')
        self.assertEqual(rv.status_code, 200)
        data = json.loads(rv.data.decode())
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Timmy')
        self.assertEqual(data[0]['admin'], True)
        self.assertEqual(data[0]['id'], 42)