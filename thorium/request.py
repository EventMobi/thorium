from urllib import parse
from .resources import ResourceManager


class Request(object):

    def __init__(self, method, identifiers, resource, query_params, body, mimetype):
        self.resource = resource
        self.method = method.lower()
        self.identifiers = identifiers
        self.params = ResourceManager(resource).get_parameters(query_params) #right way to do this?
        self.body = body
        self.mimetype = mimetype



