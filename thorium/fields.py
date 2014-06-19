from . import errors, validators, NotSet


class ResourceField(object):
    validator_type = None
    order_counter = 0

    def __init__(self, default=NotSet, notnull=False, readonly=False, writeonly=False, options=None, *args, **kwargs):
        self.flags = {
            'notnull': notnull,
            'readonly': readonly,
            'default': default,
            'writeonly': writeonly,
            'options': options
        }

        self.name = 'noname'

        self.order_value = ResourceField.order_counter
        ResourceField.order_counter += 1

        # a hook to allow subclasses to add their own unique parameters
        self.set_unique_attributes(**kwargs)

        # create validator
        self._validator = self._get_validator()
        self.flags['default'] = self._validator.validate(default, cast=False)
        self._value = self.flags['default']

    def __str__(self):
        return '{0}:{1}'.format(self.__class__.__name__, self.name)

    def set(self, value, cast=False):
        self._value = self.validate(value, cast)
        return self._value

    def get(self):
        return self._value

    def validate(self, value, cast=False):
        return self._validator.validate(value, cast)

    def to_default(self):
        return self.set(self.flags['default'])

    @property
    def is_set(self):
        return self._value != NotSet

    @property
    def is_readonly(self):
        return self.flags['readonly']

    def set_unique_attributes(self, **kwargs):
        pass

    def _get_validator(self):
        if self.validator_type:
            vt_cls = self.validator_type
            return vt_cls(self)
        else:
            raise NotImplementedError('Base class ResourceField has no validator')


class CharField(ResourceField):
    validator_type = validators.CharValidator

    def set_unique_attributes(self, max_length=None):
        self.flags['max_length'] = max_length


class IntField(ResourceField):
    validator_type = validators.IntValidator


class DecimalField(ResourceField):
    validator_type = validators.DecimalValidator


class DateField(ResourceField):
    validator_type = validators.DateValidator

    def set(self, value, cast=True, check_readonly=True):
        """
        DateField defaults cast to True since serialized data won't be in a python datetime format.
        """
        return super().set(value, cast)


class DateTimeField(ResourceField):
    validator_type = validators.DateTimeValidator

    def set(self, value, cast=True, check_readonly=False):
        """
        DateTimeField defaults cast to True since serialized data won't be in a python datetime format.
        """
        return super().set(value, cast)


class BoolField(ResourceField):
    validator_type = validators.BoolValidator


class ListField(ResourceField):
    validator_type = validators.ListValidator

    def set_unique_attributes(self, item_type=NotSet):
        if item_type:
            if item_type == NotSet or not isinstance(item_type, ResourceField):
                raise errors.ValidationError('ListField must have an item_type set to a valid ResourceField')
            self.flags['item_type'] = item_type
        else:
            self.flags['item_type'] = None


class DictField(ResourceField):
    validator_type = validators.DictValidator


class SetField(ResourceField):
    validator_type = validators.SetValidator

    def set(self, value, cast=True):
        return super().set(value, cast)
