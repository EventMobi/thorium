routes = []


def add(route):
    routes.append(route)


def add(path, resource):
    routes.append(Route(path, resource))


def endpoint(path):
    def _resource_add_route(resource):
        add(path, resource)
    return _resource_add_route


class Route(object):

    def __init__(self, path, resource):
        self.path = path
        self.resource = resource