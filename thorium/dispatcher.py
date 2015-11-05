# -*- coding: utf-8 -*-

from . import errors
from .response import DetailResponse, CollectionResponse
from .serializer import JsonSerializer


class DispatcherBase(object):
    """
    The Dispatcher holds a :class:`.ResourceInterface` and :class:`.Endpoint`
    pairing and is associated with a :class:`.Route`. It's responsible for
    handing a request off to the correct components.

    :param resource_cls: A :class:`.Resource` class definition
    :param engine: A :class:`.Endpoint` object to implement the
        :class:`.ResourceInterface`
    """

    def __init__(self, endpoint_cls, resource_cls, parameters_cls,
                 allowed_methods):
        self.Endpoint = endpoint_cls
        self.Resource = resource_cls
        self.Parameters = parameters_cls
        self.allowed_methods = {method.upper() for method in allowed_methods}

    def dispatch(self, request):
        """
        Injects the :class:`.ResourceInterface` into the :class:`.Endpoint`
        then calls a method on the engine to handle the request based on the
        :class:`.ThoriumRequest`.

        :param request: A :class:`.ThoriumRequest` object
        """

        # ensure valid method
        if request.method not in self.allowed_methods:
            msg = ('Method {0} not available on {1} {2} resource.'
                   .format(request.method,
                           self.Resource.__name__,
                           self.request_type))
            raise errors.MethodNotAllowedError(
                message=msg, headers={'Allow': ', '.join(self.allowed_methods)}
            )

        response = self.build_response_obj(request=request)

        engine = self.Endpoint(request=request, response=response)

        dispatch_method = self.get_dispatch_method(engine=engine)

        engine.authenticate(dispatch_method)

        engine.pre_request()

        self.pre_request(engine=engine)

        # Call into the endpoint
        method_response = dispatch_method()

        # Override default response
        if method_response:
            response = method_response

        engine.post_request()

        serializer = self.get_serializer()
        serialized_body = serializer.serialize_response(response)

        return response, serialized_body

    def get_dispatch_method(self, engine):
        """ find the method in the engine that matches the request """
        return getattr(engine, "{0}_{1}".format(engine.request.method.lower(),
                                                self.request_type))

    def get_serializer(self):
        return JsonSerializer()


class CollectionDispatcher(DispatcherBase):
    """
    A subclass of :class:`.DispatcherBase` to handle requests made on
    collections of :class:`.Resource`'s
    """
    request_type = 'collection'

    def pre_request(self, engine):
        engine.pre_request_collection()

    def build_response_obj(self, request):
        method = request.method.lower()
        if method == 'post':
            response = DetailResponse(request)
        else:
            response = CollectionResponse(request=request)
        return response


class DetailDispatcher(DispatcherBase):
    """
    A subclass of :class:`.DispatcherBase` to handle requests made on
    individual :class:`.Resource`'s
    """
    request_type = 'detail'

    def pre_request(self, engine):
        engine.pre_request_detail()

    def build_response_obj(self, request):
        return DetailResponse(request)
