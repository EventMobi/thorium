import urlparse
from .resources import ResourceManager


class Request(object):

    def __init__(self, method, identifiers, resource, query_string):
        self.method = method.lower()
        self.identifiers = identifiers
        self.params = self.build_params(resource, query_string)

    #Should this be here?
    @staticmethod
    def build_params(resource, query_string):
        #convert query string to dictionary of name / values
        query_dict = {name: param for name, param in urlparse.parse_qsl(query_string)}

        #return ResourceParam dictionary
        return ResourceManager(resource).get_parameters(query_dict)



