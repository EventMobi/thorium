"""
    thorium.routing
    ~~~~~~~~~~~~~~~

    This module is a helper for building and holding :class:`.Route` objects before
    they are pulled in by the :class:`.Thorium` object when it initializes.

"""

from . import dispatcher


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
        """ Adds a :class:`.Route` to internal tracking

        :param route: A :class:`.Route` class to track
        """

        self._routes.append(route)

    def get_all_routes(self):
        """ Returns all :class:`.Route`'s that have been added """

        return self._routes

    def register_resource(self, resource_cls):
        """ A convenience method to register a resource by using the default :class:`.Dispatcher`
        and :class:`.Route`. Calls :func:`add_route` for the actual adding.
        """
        #register collection route
        collection_dsp = dispatcher.CollectionDispatcher(resource_cls=resource_cls, engine_cls=resource_cls.Meta.engine, allowed_methods=resource_cls.Meta.collection_methods)
        col_route = Route('{0}_{1}'.format(resource_cls.__name__, collection_dsp.request_type), resource_cls.Meta.collection_endpoint, collection_dsp)
        self.add_route(col_route)

        #register detail route
        detail_dsp = dispatcher.DetailDispatcher(resource_cls=resource_cls, engine_cls=resource_cls.Meta.engine, allowed_methods=resource_cls.Meta.detail_methods)
        detail_route = Route('{0}_{1}'.format(resource_cls.__name__, detail_dsp.request_type), resource_cls.Meta.detail_endpoint, detail_dsp)
        self.add_route(detail_route)

        return {'collection_route': col_route, 'detail_route': detail_route}

