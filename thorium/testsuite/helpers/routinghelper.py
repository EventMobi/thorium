from thorium import Route, RouteManager, Dispatcher
from thorium.testsuite.helpers.commonhelper import Stub, ReachedMethod
from thorium.testsuite.helpers import resourcehelper, enginehelper


class RouteStub(Stub):

    def __init__(self, *args, **kwargs):
        super(RouteStub, self).__init__(Route)


class DispatcherStub(Stub):

    def __init__(self, *args, **kwargs):
        super(DispatcherStub, self).__init__(Dispatcher)


def get_test_route():
    return _build_test_route('testroute', '/testapi/testroute')


def get_test_route_manager():
    return RouteManager()


def get_test_dispatcher():
    res = resourcehelper.TestResourceInterface
    return Dispatcher(res, res.Meta.engine)


def populate_test_routes(route_manager):
    route_manager.add_route(_build_test_route('testroute1', '/testapi/testroute1'))
    route_manager.add_route(_build_test_route('testroute2', '/testapi/testroute2'))
    route_manager.add_route(_build_test_route('testroute3', '/testapi/testroute3'))


def _build_test_route(name, path):
    r = None
    try:
        r = Route(name, path, DispatcherStub())
    except ReachedMethod as reached_method:
        reached_method.expected(Dispatcher.__init__)
    return r
