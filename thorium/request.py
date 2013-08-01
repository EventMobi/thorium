import copy


class Request(object):

    def __init__(self, method, identifiers, resource_cls, query_params, mimetype, resource, request_type, url):
        self.resource_cls = resource_cls
        self.method = method
        self.identifiers = identifiers
        self.params = _get_params(resource_cls, query_params)
        self.mimetype = mimetype
        self.resource = resource
        self.request_type = request_type
        self.url = url


def _get_params(resource_cls, query_params):
    param_dict = copy.deepcopy(resource_cls.query_parameters)
    for name, param in param_dict.items():
        param.set(query_params[name]) if name in query_params else param.to_default()
    return param_dict
