from . import errors, NotSet, fields, params


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

        for name, param in input_params.items():
            if name not in cls._params:
                raise errors.ValidationError(name + ' is not a supported query parameter.')

        for name, param in cls._params.items():
            if name in input_params:
                params_dict[name] = param.validate(input_params[name])
            else:
                default = param.default()
                if default is not NotSet:
                    params_dict[name] = default
        return params_dict
