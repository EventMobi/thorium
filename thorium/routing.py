"""
    thorium.routing
    ~~~~~~~~~~~~~~~

    This module is a helper for building and holding :class:`.Route` objects before
    they are pulled in by the :class:`.Thorium` object when it initializes.

"""

import json
from .resources import ResourceManager


class Route(object):
    """ An object to hold the relationship between a url path and the
    dispatcher that handles requests to that path.

    Note: To add a route after creation use the :meth:`add_route` method.

    :param name: The name to associate with this route
    :param endpoint: The relative to base url path to access the resource, also known as the endpoint
    :param dispatcher: A :class:`.Dispatcher` object to handle the request
    """

    def __init__(self, name, endpoint, dispatcher):
        self.name = name
        self.endpoint = endpoint
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

    def register_resource(self, resource):
        """ A convenience method to register a resource by using the default :class:`.Dispatcher`
        and :class:`.Route`. Calls :func:`add_route` for the actual adding.
        """
        dsp = Dispatcher(resource, resource.Meta.engine)
        route = Route(resource.__name__, resource.Meta.endpoint, dsp)
        self.add_route(route)

        return route


class Dispatcher(object):
    """ The Dispatcher holds a :class:`.ResourceInterface` and :class:`.Engine` pairing and is associated
    with a :class:`.Route`. It's responsible for handing a request off to the correct components.

    :param resource: A :class:`.ResourceInterface` object
    :param engine: A :class:`.Engine` object to implement the :class:`.ResourceInterface`
    """

    def __init__(self, resource, engine):
        self.resource = resource
        self.engine = engine

    def dispatch(self, request):
        """ Injects the :class:`.ResourceInterface` into the :class:`.Engine`
        then calls a method on the engine to handle the request based
        on the :class:`.ThoriumRequest`.

        :param request: A :class:`.ThoriumRequest` object
        """

        #Taken from Tastypie, check that:
        #the requested HTTP method is in allowed_methods (method_check),
        #the class has a method that can handle the request (get_list),
        #the user is authenticated (is_authenticated),
        #the user is authorized (is_authorized),
        #the user has not exceeded their throttle (throttle_check).

        eng = self.engine(request)

        eng.pre_request()

        #ensure valid method
        if request.method not in {'get', 'post', 'put', 'delete', 'patch', 'options'}:
            raise NotImplementedError() #Note: make a better exception here

        #find the method in the engine that matches the request
        method = getattr(eng, str(request.method))
        result = method()

        eng.post_request()

        #Clean this up
        resource_manager = ResourceManager(self.resource)
        serializer = Serializer()
        if isinstance(result, list):
            resources = resource_manager.collection_from_native(result)
            result = serializer.serialize_collection(resources)
        else:
            resource = resource_manager.detail_from_native(result)
            result = serializer.serialize_detail(resource)

        return result


#move this to it's own file, make it good not bad
class Serializer(object):

    def serialize_detail(self, resource):
        data = {name: field.get() for (name, field) in resource.fields.items()}
        return json.dumps(data)

    def serialize_collection(self, resource_collection):
        data = []
        for resource in resource_collection:
            data.append({name: field.get() for (name, field) in resource.fields.items()})
        return json.dumps(data)