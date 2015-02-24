from . import errors, validators, NotSet


class ResourceParam(object):
    validator_type = None
    order_counter = 0

    def __init__(self, default=NotSet, notnull=False, options=None, *args, **kwargs):
        self.flags = {'notnull': notnull, 'default': default, 'options': options, 'required': False}
        self.name = 'noname'

        self.order_value = ResourceParam.order_counter
        ResourceParam.order_counter += 1

        # a hook to allow subclasses to add their own unique parameters
        self.set_unique_attributes(**kwargs)

        # create validator
        self._validator = self._get_validator()
        self.flags['default'] = self._validator.validate(default, cast=False)

    def __str__(self):
        return '{0}:{1}'.format(self.__class__.__name__, self.name)

    def validate(self, value, cast=True):
        return self._validator.validate(value, cast=cast)

    def default(self):
        return self.flags['default']

    def set_unique_attributes(self, **kwargs):
        pass

    def _get_validator(self):
        if self.validator_type:
            vt_cls = self.validator_type
            return vt_cls(self)
        else:
            raise NotImplementedError('Base class ResourceParam has no validator')


class CharParam(ResourceParam):
    validator_type = validators.CharValidator

    def set_unique_attributes(self, max_length=None):
        self.flags['max_length'] = max_length

    def validate(self, value, cast=False):
        """
        Because strings are expected, we don't want to cast
        """
        return super().validate(value, cast)


class IntParam(ResourceParam):
    validator_type = validators.IntValidator


class DecimalParam(ResourceParam):
    validator_type = validators.DecimalValidator


class DateParam(ResourceParam):
    validator_type = validators.DateValidator


class DateTimeParam(ResourceParam):
    validator_type = validators.DateTimeValidator


class BoolParam(ResourceParam):
    validator_type = validators.BoolValidator


class ListParam(ResourceParam):
    validator_type = validators.ListValidator

    def set_unique_attributes(self, item_type=None):
        if item_type:
            if item_type == validators.NotSet or not isinstance(item_type, ResourceParam):
                raise errors.ValidationError('ListParam must have an item_type set to a valid ResourceParam')
            self.flags['item_type'] = item_type
        else:
            self.flags['item_type'] = None

class JSONParam(ResourceParam):
    """A JSON resource param type.

    :param schema: Optional dict with JSON schema as per json-schema.org
    """
    validator_type = validators.JSONValidator

    def set_unique_attributes(self, schema=None):
        if schema:
            self.flags['json_schema'] = schema
