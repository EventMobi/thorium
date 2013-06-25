from flask import Flask
from unittest import TestCase
from thorium import ThoriumFlask, RouteManager
from thorium.testsuite.helpers import resourcehelper
import json
from datetime import date
import calendar


class TestThoriumFlask(TestCase):

    def setUp(self):
        route_manager = RouteManager()
        route_manager.register_resource(resourcehelper.TestResourceInterface2)
        route_manager.register_resource(resourcehelper.TestResourceInterface3)
        self.flask_app = Flask(__name__)
        ThoriumFlask(
            settings={},
            route_manager=route_manager,
            flask_app=self.flask_app
        )

    def test_simple_detail_get(self):
        rv = self.flask_app.test_client().open('/testapi/testresource/1', method='GET')
        self.assertEqual(rv.status_code, 200)
        data = json.loads(rv.data)
        self.assertEqual(data['name'], 'Timmy')
        self.assertEqual(data['age'], 1)
        self.assertEqual(data['birth_date'], calendar.timegm(date(2012, 3, 13).timetuple()))
        self.assertEqual(data['admin'], True)

    def test_simple_list_get(self):
        rv = self.flask_app.test_client().open('/testapi/testresource', method='GET')
        self.assertEqual(rv.status_code, 200)
        data = json.loads(rv.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Timmy')
        self.assertEqual(data[0]['age'], 1)
        self.assertEqual(data[0]['birth_date'], calendar.timegm(date(2012, 3, 13).timetuple()))
        self.assertEqual(data[0]['admin'], True)