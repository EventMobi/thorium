import unittest
from thorium.testsuite.helpers import routinghelper, resourcehelper, enginehelper, requesthelper
from thorium.testsuite.helpers.commonhelper import ReachedMethod
from thorium import Engine


class TestRoute(unittest.TestCase):

    def setUp(self):
        self.route = routinghelper.get_test_route()

    def test_init(self):
        self.assertEqual(self.route.name, 'testroute')
        self.assertEqual(self.route.endpoint, '/testapi/testroute')
        self.assertEqual(self.route.dispatcher.__class__, routinghelper.DispatcherStub)


class TestRouteManager(unittest.TestCase):

    def setUp(self):
        self.route_manager = routinghelper.get_test_route_manager()

    def test_init(self):
        self.assertFalse(self.route_manager._routes, '_routes should be empty')

    def test_add_route(self):
        route = routinghelper.get_test_route()
        self.route_manager.add_route(route)
        self.assertIn(route, self.route_manager._routes, 'new route should be in _routes')

    def test_get_all_routes(self):
        routinghelper.populate_test_routes(self.route_manager)
        routes = self.route_manager.get_all_routes()
        for r in routes:
            self.assertIn(r, self.route_manager._routes, 'retrieved routes should be the same as in _routes')

    def test_register_resource(self):
        test_res = resourcehelper.TestResourceInterface
        route = self.route_manager.register_resource(test_res)

        self.assertEqual(route.endpoint, test_res.Meta.endpoint,
                         'route endpoint should be taken from resource')
        self.assertEqual(route.dispatcher.engine, test_res.Meta.engine,
                         'dispatcher engine should be taken from resource')
        self.assertIn(route, self.route_manager._routes,
                      'the new route should be present in the route_manager _routes')

    def _populate_routes(self):
        self.route_manager.add_route()


class TestDispatcher(unittest.TestCase):

    def setUp(self):
        self.dispatcher = routinghelper.get_test_dispatcher()

    def test_init(self):
        self.assertEqual(self.dispatcher.resource, resourcehelper.TestResourceInterface)
        self.assertEqual(self.dispatcher.engine, enginehelper.EngineStub)

    def test_dispatch_get(self):
        request = requesthelper.get_test_request('get')
        with self.assertRaises(ReachedMethod) as cm:
            self.dispatcher.dispatch(request)
        self.assertTrue(cm.exception.expected(Engine.get))

    def test_dispatch_post(self):
        request = requesthelper.get_test_request('post')
        with self.assertRaises(ReachedMethod) as cm:
            self.dispatcher.dispatch(request)
        self.assertTrue(cm.exception.expected(Engine.post))

    def test_dispatch_put(self):
        request = requesthelper.get_test_request('put')
        with self.assertRaises(ReachedMethod) as cm:
            self.dispatcher.dispatch(request)
        self.assertTrue(cm.exception.expected(Engine.put))

    def test_dispatch_delete(self):
        request = requesthelper.get_test_request('delete')
        with self.assertRaises(ReachedMethod) as cm:
            self.dispatcher.dispatch(request)
        self.assertTrue(cm.exception.expected(Engine.delete))

    def test_dispatch_patch(self):
        request = requesthelper.get_test_request('patch')
        with self.assertRaises(ReachedMethod) as cm:
            self.dispatcher.dispatch(request)
        self.assertTrue(cm.exception.expected(Engine.patch))

    def test_dispatch_options(self):
        request = requesthelper.get_test_request('options')
        with self.assertRaises(ReachedMethod) as cm:
            self.dispatcher.dispatch(request)
        self.assertTrue(cm.exception.expected(Engine.options))

    def test_dispatch_not_implemented(self):
        request = requesthelper.get_test_request('invalid_verb')
        with self.assertRaises(NotImplementedError):
            self.dispatcher.dispatch(request)
