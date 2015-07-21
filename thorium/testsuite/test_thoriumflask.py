# -*- coding: utf-8 -*-

import unittest
import json
import datetime

from collections import OrderedDict

from flask import Flask

from thorium import (
    ThoriumFlask,
    RouteManager,
    Resource,
    fields,
    Endpoint,
)

routing = RouteManager()


class PersonResource(Resource):
    id = fields.IntField(default=None)
    name = fields.CharField()
    birth_date = fields.DateTimeField()
    admin = fields.BoolField(default=False)


class CollectionParams(Resource):
    times = fields.IntField(required=True, default=1)


@routing.collection(path='/api/event/<int:event_id>/people',
                    methods=('get', 'post'),
                    parameters_cls=CollectionParams)
@routing.detail(path='/api/event/<int:event_id>/people/<int:id>',
                methods=('get', 'put', 'patch'))
class PersonEndpoint(Endpoint):
    Resource = PersonResource

    def pre_request(self):
        self.data = {
            'id': 42,
            'name': 'Timmy',
            'birth_date': datetime.datetime(1974, 3, 13),
            'admin': True
        }

    def get_detail(self):
        person = PersonResource(self.data)
        self.response.resource = person

    def get_collection(self):
        for x in range(self.request.params.times):
            self.data['id'] = x
            person = PersonResource(self.data)
            self.response.resources.append(person)

    def post_collection(self):
        res = self.request.resource
        name = res.name
        birth_date = res.birth_date
        admin = res.admin
        self.response.location_header(4)


class TestThoriumFlask(unittest.TestCase):

    def setUp(self):
        self.flask_app = Flask(__name__)
        ThoriumFlask(
            settings={},
            route_manager=routing,
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
        self.assertEqual(meta, {
                                'pagination': {
                                    'limit': None,
                                    'offset': None,
                                    'paginated': False,
                                    'record_count': 0
                                    }
                                })
        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['name'], 'Timmy')
        self.assertEqual(items[0]['admin'], True)
        self.assertEqual(items[0]['id'], 0)

    def test_get_with_query_param(self):
        rv = self.c.open('/api/event/1/people?times=1', method='GET')
        self.assertEqual(rv.status_code, 200)
        rv = self.c.open('/api/event/1/people?invalid=1', method='GET')
        self.assertEqual(rv.status_code, 400)
        rv = self.c.open('/api/event/1/people?times=1&invalid=1', method='GET')
        self.assertEqual(rv.status_code, 400)

    def test_get_with_sort(self):
        rv = self.c.open('/api/event/1/people?times=5&sort=-id', method='GET')
        self.assertEqual(rv.status_code, 200)
        body = json.loads(rv.data.decode())
        items = body['data']
        meta = body['meta']
        self.assertDictEqual(meta, {
                'sort': '-id',
                'pagination': {
                    'limit': None,
                    'offset': None,
                    'paginated': False,
                    'record_count': 0
                }})
        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 5)
        for x in range(5):
            self.assertDictEqual(items[x], {
                'id': 4 - x,
                'name': 'Timmy',
                'birth_date': '1974-03-13T00:00:00',
                'admin': True
            })

    def test_get_with_sort_multiple(self):
        rv = self.c.open('/api/event/1/people?times=5&sort=-name,-id',
                         method='GET')
        self.assertEqual(rv.status_code, 200)
        body = json.loads(rv.data.decode())
        items = body['data']
        meta = body['meta']
        self.assertDictEqual(meta, {
                                    'sort': '-name,-id',
                                    'pagination': {
                                        'limit': None,
                                        'offset': None,
                                        'paginated': False,
                                        'record_count': 0
                                        }
                                    })
        self.assertEqual(len(items), 5)
        for x in range(5):
            self.assertDictEqual(items[x], {
                'id': 4 - x,
                'name': 'Timmy',
                'birth_date': '1974-03-13T00:00:00',
                'admin': True
            })

    def test_get_with_sort_mixed(self):
        rv = self.c.open('/api/event/1/people?times=5&sort=name,-id',
                         method='GET')
        self.assertEqual(rv.status_code, 200)
        body = json.loads(rv.data.decode())
        items = body['data']
        print(body)
        meta = body['meta']
        self.assertDictEqual(meta, {
                                    'sort': 'name,-id',
                                    'pagination': {
                                        'limit': None,
                                        'offset': None,
                                        'paginated': False,
                                        'record_count': 0
                                        }
                                    })
        self.assertEqual(len(items), 5)
        for x in range(5):
            self.assertDictEqual(items[x], {
                'id': 4 - x,
                'name': 'Timmy',
                'birth_date': '1974-03-13T00:00:00',
                'admin': True
            })

    def test_get_with_sort_invalid(self):
        rv = self.c.open('/api/event/1/people?times=5&sort=+YO', method='GET')
        self.assertEqual(rv.status_code, 400)

        rv = self.c.open('/api/event/1/people?times=5&sort=+id,None',
                         method='GET')
        self.assertEqual(rv.status_code, 400)

    def test_get_with_pagination(self):
        rv = self.c.open('/api/event/1/people?times=5&offset=2&limit=2',
                         method='GET')
        self.assertEqual(rv.status_code, 200)
        body = json.loads(rv.data.decode())
        items = body['data']
        meta = body['meta']
        self.assertDictEqual(
            meta,
            {
                'limit': 2,
                'offset': 2,
                'pagination': {
                    'limit': 2,
                    'offset': 2,
                    'paginated': False,
                    'record_count': 0,
                }
            }
        )
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]['id'], 2)
        self.assertEqual(items[1]['id'], 3)

        rv = self.c.open('/api/event/1/people?times=5&offset=5&limit=10',
                         method='GET')
        self.assertEqual(rv.status_code, 200)
        body = json.loads(rv.data.decode())
        items = body['data']
        meta = body['meta']
        self.assertDictEqual(
            meta,
            {
                'limit': 10,
                'offset': 5,
                'pagination': {
                    'limit': 10,
                    'offset': 5,
                    'paginated': False,
                    'record_count': 0,
                }
            })
        self.assertEqual(items, [])

    def test_get_with_pagination_invalid(self):
        rv = self.c.open('/api/event/1/people?times=5&offset=-1&limit=5',
                         method='GET')
        self.assertEqual(rv.status_code, 400)

        rv = self.c.open('/api/event/1/people?times=5&offset=0&limit=0',
                         method='GET')
        self.assertEqual(rv.status_code, 400)

        rv = self.c.open('/api/event/1/people?times=5&offset=True&limit=1',
                         method='GET')
        self.assertEqual(rv.status_code, 400)

        rv = self.c.open('/api/event/1/people?times=5&offset=hello&limit=5',
                         method='GET')
        self.assertEqual(rv.status_code, 400)

    def test_get_with_sort_and_pagination(self):
        rv = self.c.open(
            '/api/event/1/people?times=5&sort=-id&offset=2&limit=2',
            method='GET'
        )
        self.assertEqual(rv.status_code, 200)
        body = json.loads(rv.data.decode())
        items = body['data']
        meta = body['meta']
        self.assertDictEqual(meta, {
                                    'sort': '-id',
                                    'offset': 2,
                                    'limit': 2,
                                    'pagination': {
                                        'limit': 2,
                                        'offset': 2,
                                        'paginated': False,
                                        'record_count': 0,
                                        },
                                    })
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]['id'], 2)
        self.assertEqual(items[1]['id'], 1)

    def test_post_simple(self):
        data = {
            'name': 'Snoopy',
            'birth_date': datetime.datetime(1974, 3, 13),
            'admin': True
        }
        rv = self.c.post('/api/event/1/people',
                         data=json.dumps(data, default=handler),
                         content_type='application/json')
        self.assertEqual(rv.status_code, 201)

    def test_post_partial_resource(self):
        data = {
            'birth_date': datetime.datetime(1974, 3, 13),
            'admin': True
        }
        rv = self.c.post('/api/event/1/people',
                         data=json.dumps(data, default=handler),
                         content_type='application/json')
        self.assertEqual(rv.status_code, 400)

    def test_envelope_field_order(self):
        rv = self.c.open('/api/event/1/people/1', method='GET')
        self.assertEqual(rv.status_code, 200)
        od = json.loads(rv.data.decode(), object_pairs_hook=OrderedDict)
        self.assertEqual(od.popitem(last=False)[0], 'type')
        self.assertEqual(od.popitem(last=False)[0], 'status')
        self.assertEqual(od.popitem(last=False)[0], 'error')
        self.assertEqual(od.popitem(last=False)[0], 'data')
        self.assertEqual(od.popitem(last=False)[0], 'meta')

    def test_field_order_matches_resource(self):
        rv = self.c.open('/api/event/1/people/1', method='GET')
        self.assertEqual(rv.status_code, 200)
        od = json.loads(rv.data.decode(), object_pairs_hook=OrderedDict)
        data = od['data']
        self.assertEqual(data.popitem(last=False)[0], 'id')
        self.assertEqual(data.popitem(last=False)[0], 'name')
        self.assertEqual(data.popitem(last=False)[0], 'birth_date')
        self.assertEqual(data.popitem(last=False)[0], 'admin')

    def test_post_empty_body(self):
        rv = self.c.post('/api/event/1/people',
                         data=json.dumps({}, default=handler),
                         content_type='application/json')
        self.assertEqual(rv.status_code, 400)

    def test_post_no_body(self):
        rv = self.c.post('/api/event/1/people',
                         data=None,
                         content_type='application/json')
        self.assertEqual(rv.status_code, 400)


class TestResourceSpeed(unittest.TestCase):

    def setUp(self):
        self.flask_app = Flask(__name__)
        ThoriumFlask(
            settings={},
            route_manager=routing,
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
                rv = self.c.open('/api/event/1/people?times={0}'.format(y),
                                 method='GET')
                times.append(time.time() - start_time)
                self.assertEqual(rv.status_code, 200)
            print('{0} - avg time: {1}'.format(y, sum(times) / len(times)))


def handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError(
            'Object of type %s with value of %s is not JSON serializable' %
            (type(obj), repr(obj))
        )
