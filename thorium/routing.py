"""
    thorium.routing
    ~~~~~~~~~~~~~~~

    This module is a helper for building and holding :class:`.Route` objects before
    they are pulled in by the :class:`.Thorium` object when it initializes.

"""

_routes = []


def add_route(route):
    """ Adds a :class:`.Route` to internal tracking

    :param route: A :class:`.Route` class to track
    """

    _routes.append(route)


def get_all_routes():
    """ Returns all :class:`.Route`'s that have been added """

    return _routes


class Route(object):
    """ An object to hold the relationship between a url path and the
    dispatcher that handles requests to that path.

    Note: To add a route after creation use the :meth:`add_route` method.

    :param name: The name to associate with this route
    :param path: The relative to base url path to access the resource, also known as the endpoint
    :param dispatcher: A :class:`.Dispatcher` object to handle the request
    """

    def __init__(self, name, path, dispatcher):
        self.name = name
        self.path = path
        self.dispatcher = dispatcher