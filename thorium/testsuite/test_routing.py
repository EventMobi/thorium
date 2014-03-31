import unittest
from unittest import mock
from thorium import Endpoint, Resource, Route, RouteManager, dispatcher


class TestRouteManager(unittest.TestCase):

    def setUp(self):
        self.route_manager = RouteManager()

    def test_init(self):
        self.assertFalse(self.route_manager._routes, '_routes should be empty')

    def test_add_route(self):
        route = mock.MagicMock(spec=Route)
        self.route_manager.add_route(route)
        self.assertIn(route, self.route_manager._routes, 'new route should be in _routes')

    def test_get_all_routes(self):
        route1 = mock.MagicMock(spec=Route)
        route2 = mock.MagicMock(spec=Route)
        self.route_manager.add_route(route1)
        self.route_manager.add_route(route2)
        routes = self.route_manager.get_all_routes()
        self.assertIn(route1, routes)
        self.assertIn(route2, routes)

    def test_register_resource(self):
        resource = mock.MagicMock()
        resource.__name__ = 'res'
        endpoint = mock.MagicMock()
        endpoint.__name__ = 'ep'
        route1 = mock.MagicMock(spec=Route)
        route2 = mock.MagicMock(spec=Route)
        endpoint.routes = [route1, route2]
        self.route_manager.register_endpoint(endpoint)

        #newly created routes should be internally tracked by the route_manager
        routes = self.route_manager.get_all_routes()
        self.assertIn(route1, routes)
        self.assertIn(route2, routes)