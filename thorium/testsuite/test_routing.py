import unittest
from unittest import mock
from thorium import Engine, Resource, Route, RouteManager, dispatcher


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
        engine = mock.MagicMock()
        resource.__name__ = 'res'
        route_dict = self.route_manager.register_endpoint(resource, engine)

        #register_resource should return a collection_route and detail_route
        col_route = route_dict['collection_route']
        det_route = route_dict['detail_route']
        self.assertIsInstance(col_route, Route)
        self.assertIsInstance(det_route, Route)

        #each route should have a reference to the appropriate dispatcher
        self.assertIsInstance(col_route.dispatcher, dispatcher.CollectionDispatcher)
        self.assertIsInstance(det_route.dispatcher, dispatcher.DetailDispatcher)

        #newly created routes should be internally tracked by the route_manager
        routes = self.route_manager.get_all_routes()
        self.assertIn(col_route, routes)
        self.assertIn(det_route, routes)