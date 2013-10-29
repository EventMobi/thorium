import copy


class Request(object):

    def __init__(self, method, identifiers, resource_cls, query_params, mimetype, resource, request_type, url):
        self.method = method
        self.identifiers = identifiers
        self.resource_cls = resource_cls
        self.params = _get_params(resource_cls, query_params)
        self.mimetype = mimetype
        self.resource = resource
        self.request_type = request_type
        self.url = url


def _get_params(resource_cls, query_params):
    params_dict = {}
    resource_params = copy.deepcopy(resource_cls.query_parameters)
    for name, param in resource_params.items():
        param.set(query_params[name]) if name in query_params else param.to_default()
        if param.is_set():
            params_dict[name] = param.get()
    return params_dict
