class Request(object):

    def __init__(self, dispatcher, method, identifiers, query_params, mimetype, resource, resources, url):
        self.method = method
        self.identifiers = identifiers
        self.params = query_params
        self.mimetype = mimetype
        self.resource = resource
        self.resources = resources
        self.request_type = dispatcher.request_type
        self.url = url
