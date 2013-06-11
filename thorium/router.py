from dispatcher import Dispatcher

routes = []


def add_route(route):
    routes.append(route)


def create_route(name, path, dispatcher):
    return Route(name, path, dispatcher)


def create_dispatcher(resource, engine):
    return Dispatcher(resource, engine)


def endpoint(path):
    def _register_endpoint(resource):
        dsp = create_dispatcher(resource, resource.Meta.engine)
        route = create_route(resource.__name__, path, dsp)
        add_route(route)
    return _register_endpoint


class Route(object):

    def __init__(self, name, path, dispatcher):
        self.name = name
        self.path = path
        self.dispatcher = dispatcher