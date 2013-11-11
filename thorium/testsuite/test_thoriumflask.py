from flask import Flask
import unittest
from unittest import mock
from thorium import ThoriumFlask, RouteManager, Resource, fields, Engine
import json
import datetime
import calendar


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
        collection = {
            'endpoint': '/api/event/<int:event_id>/people',
            'methods': {'get', 'post'}
        }

        detail = {
            'endpoint': '/api/event/<int:event_id>/people/<int:id>',
            'methods': {'get', 'put', 'patch'}
        }


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

    def post_collection(self):
        res = self.request.resource
        name = res.name
        birth_date = res.birth_date
        admin = res.admin
        self.response.location_header(4)


class DataStore(object):

    def populate_person(self, person):
        person.id = 42
        person.name = 'Timmy'
        person.birth_date = datetime.datetime(1974, 3, 13)
        person.admin = True


class TestThoriumFlask(unittest.TestCase):

    def setUp(self):
        route_manager = RouteManager()
        route_manager.register_endpoint(PersonResource, PersonEngine)
        self.flask_app = Flask(__name__)
        ThoriumFlask(
            settings={},
            route_manager=route_manager,
            flask_app=self.flask_app
        )
        self.c = self.flask_app.test_client()

    def test_simple_detail_get(self):
        rv = self.c.open('/api/event/1/people/1', method='GET')
        self.assertEqual(rv.status_code, 200)
        data = json.loads(rv.data.decode())
        self.assertEqual(data['name'], 'Timmy')
        self.assertEqual(data['admin'], True)
        self.assertEqual(data['id'], 42)

    def test_simple_list_get(self):
        rv = self.c.open('/api/event/1/people', method='GET')
        self.assertEqual(rv.status_code, 200)
        data = json.loads(rv.data.decode())
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Timmy')
        self.assertEqual(data[0]['admin'], True)
        self.assertEqual(data[0]['id'], 42)

    def test_post_simple(self):
        data = {
            'name': 'Snoopy',
            'birth_date': datetime.datetime(1974, 3, 13),
            'admin': True
        }
        rv = self.c.post('/api/event/1/people', data=json.dumps(data, default=handler), content_type='application/json')
        self.assertEqual(rv.status_code, 201)

    def test_post_partial_resource(self):
        data = {
            'birth_date': datetime.datetime(1974, 3, 13),
            'admin': True
        }
        rv = self.c.post('/api/event/1/people', data=json.dumps(data, default=handler), content_type='application/json')
        self.assertEqual(rv.status_code, 400)


def handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    #elif isinstance(obj, ...):
    #    return ...
    else:
        raise TypeError('Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj)))