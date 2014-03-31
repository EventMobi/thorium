from flask import Flask
import unittest
from thorium import ThoriumFlask, RouteManager, Resource, fields, Endpoint, params, routing, Parameters
import json
import datetime


class PersonResource(Resource):
    id = fields.IntField(default=None)
    name = fields.CharField()
    birth_date = fields.DateTimeField()
    admin = fields.BoolField()


class CollectionParams(Parameters):
    times = params.IntParam(default=1)


@routing.collection('/api/event/<int:event_id>/people', methods=('get', 'post'), params=CollectionParams)
@routing.detail('/api/event/<int:event_id>/people/<int:id>', ('get', 'put', 'patch'))
class PersonEndpoint(Endpoint):
    resource = PersonResource

    def pre_request(self):
        self.data = {
            'id': 42,
            'name': 'Timmy',
            'birth_date': datetime.datetime(1974, 3, 13),
            'admin': True
        }

    def get_detail(self):
        person = self.request.resource_cls(self.data)
        self.response.resource = person

    def get_collection(self):
        for x in range(self.request.params['times']):
            person = self.request.resource_cls(self.data)
            self.response.resources.append(person)

    def post_collection(self):
        res = self.request.resource
        name = res.name
        birth_date = res.birth_date
        admin = res.admin
        self.response.location_header(4)


class TestThoriumFlask(unittest.TestCase):

    def setUp(self):
        route_manager = RouteManager()
        route_manager.register_endpoint(PersonEndpoint)
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
        data = json.loads(rv.data.decode())['data']
        self.assertEqual(data['name'], 'Timmy')
        self.assertEqual(data['admin'], True)
        self.assertEqual(data['id'], 42)

    def test_simple_list_get(self):
        rv = self.c.open('/api/event/1/people', method='GET')
        self.assertEqual(rv.status_code, 200)
        body = json.loads(rv.data.decode())
        items = body['data']
        meta = body['meta']
        self.assertEqual(meta, {})
        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['name'], 'Timmy')
        self.assertEqual(items[0]['admin'], True)
        self.assertEqual(items[0]['id'], 42)

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


class TestResourceSpeed(unittest.TestCase):

    def setUp(self):
        route_manager = RouteManager()
        route_manager.register_endpoint(PersonEndpoint)
        self.flask_app = Flask(__name__)
        ThoriumFlask(
            settings={},
            route_manager=route_manager,
            flask_app=self.flask_app
        )
        self.c = self.flask_app.test_client()

    def test_speed_simple(self):
        import time
        abc = [1, 10, 100]
        for y in abc:
            times = []
            for x in range(20):
                start_time = time.time()
                rv = self.c.open('/api/event/1/people?times={0}'.format(y), method='GET')
                times.append(time.time() - start_time)
                self.assertEqual(rv.status_code, 200)
            print('{0} - avg time: {1}'.format(y, sum(times) / len(times)))


def handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError('Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj)))