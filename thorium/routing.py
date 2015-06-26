"""
    thorium.routing
    ~~~~~~~~~~~~~~~

    This module is a helper for building and holding :class:`.Route` objects before
    they are pulled in by the :class:`.Thorium` object when it initializes.

"""

from . import dispatcher
from .resources import ResourceMetaClass


class Route(object):
    """ An object to hold the relationship between a url path and the
    dispatcher that handles requests to that path.

    Note: To add a route after creation use the :meth:`add_route` method.

    :param name: The name to associate with this route
    :param path: The relative to base url path to access the resource, sometimes referred to as endpoint
    :param dispatcher: A :class:`.Dispatcher` object to handle the request
    """

    def __init__(self, name, path, dispatcher):
        self.name = name
        self.path = path
        self.dispatcher = dispatcher


class RouteManager(object):
    """ Manages the list of :class:`.Route`'s needed by :class:`.Thorium`.
    Register your resources using either :func:`register_resource` or build :class:`.Route`'s
    manually and add them with :func:`add_route`.
    """

    def __init__(self):
        self._routes = []

    def add_route(self, route):
        """
        Adds a :class:`.Route` to internal tracking

        :param route: A :class:`.Route` class to track
        """
        self._routes.append(route)

    def get_all_routes(self):
        """ Returns all :class:`.Route`'s that have been added """

        return self._routes

    def collection(self, path, methods, parameters_cls=None):
        def wrapped(cls):
            route = build_route(dispatcher.CollectionDispatcher,
                                cls,
                                parameters_cls,
                                path,
                                methods)
            self._routes.append(route)
            if hasattr(cls, 'routes'):
                cls.routes.append(route)
            else:
                cls.routes = [route]
            return cls
        return wrapped

    def detail(self, path, methods, parameters_cls=None):
        def wrapped(cls):
            route = build_route(dispatcher.DetailDispatcher,
                                cls,
                                parameters_cls, path, methods)
            self._routes.append(route)
            if hasattr(cls, 'routes'):
                cls.routes.append(route)
            else:
                cls.routes = [route]
            return cls
        return wrapped


def build_route(dispatcher_cls, endpoint_cls, parameters_cls, path, methods):
    if not hasattr(endpoint_cls, 'Resource') or not isinstance(endpoint_cls.Resource, ResourceMetaClass):
        raise Exception('Endpoint {0} expects attribute resource to have a valid Resource object.'
                        .format(endpoint_cls.__name__))

    dsp = dispatcher_cls(endpoint_cls=endpoint_cls,
                         resource_cls=endpoint_cls.Resource,
                         parameters_cls=parameters_cls,
                         allowed_methods=set(methods))
    route = Route(name='{0}_{1}'.format(endpoint_cls.__name__, dsp.request_type),
                  path=path,
                  dispatcher=dsp)
    return route
