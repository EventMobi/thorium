from . import errors, NotSet, fields, params


class Endpoint(object):
    """
    Responsible for the implementation of a single :class:`Resource`,
    The methods provide hooks which will be called into by the dispatcher
    during a request.

    :param request: A :class:`Request` object.
    :param response: A :class:`Response` object.
    """

    _authenticator_classes = None
    resource = None

    def __init__(self, request, response):
        self.request = request
        self.response = response
        self._authenticators = []
        if self._authenticator_classes:
            self._authenticators = [a(self) for a in self._authenticator_classes]

    def authenticate(self, method):
        if self._authenticators:
            for auth in self._authenticators:
                auth.check_auth(method)

    def pre_request(self):
        pass

    def pre_request_detail(self):
        pass

    def pre_request_collection(self):
        pass

    def post_request(self):
        pass

    def get_detail(self):
        raise errors.MethodNotImplementedError()

    def get_collection(self):
        raise errors.MethodNotImplementedError()

    def post_detail(self):
        raise errors.MethodNotImplementedError()

    def post_collection(self):
        raise errors.MethodNotImplementedError()

    def put_detail(self):
        raise errors.MethodNotImplementedError()

    def put_collection(self):
        raise errors.MethodNotImplementedError()

    def delete_detail(self):
        raise errors.MethodNotImplementedError()

    def delete_collection(self):
        raise errors.MethodNotImplementedError()

    def patch_detail(self):
        raise errors.MethodNotImplementedError()

    def patch_collection(self):
        raise errors.MethodNotImplementedError()

    def options(self):
        raise errors.MethodNotImplementedError()


class ParametersMetaClass(type):

    def __new__(mcs, parameters_name, bases, attrs):
        params_dict = {}
        for name, param in list(attrs.items()):
            if isinstance(param, params.ResourceParam):
                param.name = name
                params_dict[name] = param
            elif isinstance(param, fields.ResourceField):
                raise Exception('Expected subclass of ResourceParam, got {0}'.format(param))
        attrs['_params'] = params_dict
        return super().__new__(mcs, parameters_name, bases, attrs)


class Parameters(object, metaclass=ParametersMetaClass):

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    @classmethod
    def validate(cls, input_params):
        params_dict = {}
        for name, param in cls._params.items():
            if name in input_params:
                params_dict[name] = param.validate(input_params[name])
            else:
                default = param.default()
                if default is not NotSet:
                    params_dict[name] = default
        return params_dict
