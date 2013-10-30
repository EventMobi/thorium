from . import errors
from .response import DetailResponse, CollectionResponse

#Taken from Tastypie, check that:
        #the requested HTTP method is in allowed_methods (method_check),
        #the class has a method that can handle the request (get_list),
        #the user is authenticated (is_authenticated),
        #the user is authorized (is_authorized),
        #the user has not exceeded their throttle (throttle_check).


class DispatcherBase(object):
    """ The Dispatcher holds a :class:`.ResourceInterface` and :class:`.Engine` pairing and is associated
    with a :class:`.Route`. It's responsible for handing a request off to the correct components.

    :param resource_cls: A :class:`.Resource` class definition
    :param engine: A :class:`.Engine` object to implement the :class:`.ResourceInterface`
    """

    def __init__(self, resource_cls, engine_cls, allowed_methods):
        self.resource_cls = resource_cls
        self.engine_cls = engine_cls
        self.allowed_methods = {method.upper() for method in allowed_methods}

    def dispatch(self, request):
        """ Injects the :class:`.ResourceInterface` into the :class:`.Engine`
        then calls a method on the engine to handle the request based
        on the :class:`.ThoriumRequest`.

        :param request: A :class:`.ThoriumRequest` object
        """

        #ensure valid method
        if request.method not in self.allowed_methods:
            msg = 'Method {0} not available on {1} {2} resource.'\
                .format(request.method, self.resource_cls.__name__, self.request_type)
            raise errors.MethodNotAllowedError(message=msg, headers={'Allow': ', '.join(self.allowed_methods)})

        response = self.build_response_obj(request=request)

        engine = self.engine_cls(request=request, response=response)

        dispatch_method = self.get_dispatch_method(engine=engine)

        engine.authenticate(dispatch_method)

        engine.pre_request()

        self.pre_request(engine=engine)

        method_response = dispatch_method()
        if method_response:
            response = method_response

        engine.post_request()

        return response

    def get_dispatch_method(self, engine):
        """ find the method in the engine that matches the request """
        return getattr(engine, "{0}_{1}".format(engine.request.method.lower(), self.request_type))


class CollectionDispatcher(DispatcherBase):
    """ A subclass of :class:`.DispatcherBase` to handle requests made on individual :class:`.Resource`'s """
    request_type = 'collection'

    def pre_request(self, engine):
        engine.pre_request_collection()

    def build_response_obj(self, request):
        return CollectionResponse(request)


class DetailDispatcher(DispatcherBase):
    """ A subclass of :class:`.DispatcherBase` to handle requests made on collections of :class:`.Resource`'s """
    request_type = 'detail'

    def pre_request(self, engine):
        engine.pre_request_detail()

    def build_response_obj(self, request):
        return DetailResponse(request)









