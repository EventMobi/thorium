from .resources import ResourceManager


class Request(object):

    def __init__(self, method, identifiers, resource_cls, query_params, mimetype, resource, request_type, url):
        self.resource_cls = resource_cls
        self.method = method
        self.identifiers = identifiers
        self.params = ResourceManager(resource_cls).get_parameters(query_params) #right way to do this?
        self.mimetype = mimetype
        self.resource = resource
        self.request_type = request_type
        self.url = url


