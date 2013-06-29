from . import serializers

#Taken from Tastypie, check that:
        #the requested HTTP method is in allowed_methods (method_check),
        #the class has a method that can handle the request (get_list),
        #the user is authenticated (is_authenticated),
        #the user is authorized (is_authorized),
        #the user has not exceeded their throttle (throttle_check).


class DispatcherBase(object):
    """ The Dispatcher holds a :class:`.ResourceInterface` and :class:`.Engine` pairing and is associated
    with a :class:`.Route`. It's responsible for handing a request off to the correct components.

    :param resource: A :class:`.ResourceInterface` object
    :param engine: A :class:`.Engine` object to implement the :class:`.ResourceInterface`
    """

    def __init__(self, resource, engine, allowed_methods):
        self.resource = resource
        self.engine = engine
        self.allowed_methods = allowed_methods

    def dispatch(self, request):
        """ Injects the :class:`.ResourceInterface` into the :class:`.Engine`
        then calls a method on the engine to handle the request based
        on the :class:`.ThoriumRequest`.

        :param request: A :class:`.ThoriumRequest` object
        """

        #ensure valid method
        if request.method not in self.allowed_methods:
            #raise 405 error, The response MUST include an Allow header containing a list of valid methods for the requested resource
            raise Exception('405: method not allowed')

        engine = self.engine(request)

        engine.pre_request()

        self.pre_request(engine)

        method = self.get_dispatch_method(request, engine)

        engine.post_request()

        if request.method in {'post', 'put', 'patch'}:
            resource = self.serializer.deserialize(request)
            method(resource)
            return ''
        elif request.method == 'delete':
            method()
            return ''
        else:
            result = method()
            result = self.serializer.serialize(result)
            return result


class CollectionDispatcher(DispatcherBase):
    """ A subclass of :class:`.DispatcherBase` to handle requests made on individual :class:`.Resource`'s """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializer = serializers.CollectionSerializer()

    def pre_request(self, engine):
        engine.pre_request_collection()

    def get_dispatch_method(self, request, engine):
        """ find the method in the engine that matches the request """
        return getattr(engine, "{meth}_collection".format(meth=request.method))


class DetailDispatcher(DispatcherBase):
    """ A subclass of :class:`.DispatcherBase` to handle requests made on collections of :class:`.Resource`'s """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializer = serializers.DetailSerializer()

    def pre_request(self, engine):
        engine.pre_request_detail()

    def get_dispatch_method(self, request, engine):
        """ find the method in the engine that matches the request """
        return getattr(engine, "{meth}_detail".format(meth=request.method))







