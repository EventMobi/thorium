import numbers
import datetime
from . import errors


#Field Validators
class FieldValidator(object):

    def __init__(self, field):
        self._field = field

    def validate(self, value, cast=False):
        if self._field.flags['notnull'] and value is None:
            raise errors.ValidationError('{0} cannot be null'.format(self._field))
        elif value is NotSet:
            return value
        elif value is not None:
            value = self._type_validation(value, cast)
        return value

    def _type_validation(self, value, cast):
        if not self.valid(value):
            if cast:
                try:
                    value = self.attempt_cast(value)
                except (ValueError, TypeError):
                    self.raise_validation_error(value)
            else:
                self.raise_validation_error(value)

        self.additional_validation(value)
        return value

    def valid(self, value):
        raise NotImplementedError()

    def attempt_cast(self, value):
        raise NotImplementedError()

    def raise_validation_error(self, value):
        raise NotImplementedError()

    def additional_validation(self, value):
        pass


class CharValidator(FieldValidator):

    def valid(self, value):
        return isinstance(value, str)

    def attempt_cast(self, value):
        return str(value)

    def raise_validation_error(self, value):
        raise errors.ValidationError('{0} expects a string, got {1}'.format(self._field, value))

    def additional_validation(self, value):
        if self._field.flags['max_length'] and len(value) > self._field.flags['max_length']:
            raise errors.ValidationError('Max length of {0} is {1}, given value was {2}'.format(
                self._field,
                self._field.flags['max_length'],
                len(value))
            )


class IntValidator(FieldValidator):

    def valid(self, value):
        return isinstance(value, numbers.Integral) and not isinstance(value, bool)

    def attempt_cast(self, value):
        return int(value)

    def raise_validation_error(self, value):
        raise errors.ValidationError('{0} expects an int or long, got {1}'.format(self._field, value))


class DecimalValidator(FieldValidator):

    def valid(self, value):
        return isinstance(value, numbers.Real) and not isinstance(value, bool)

    def attempt_cast(self, value):
        return float(value)

    def raise_validation_error(self, value):
        raise errors.ValidationError('{0} expects a number, got {1}'.format(self._field, value))


class DateTimeValidator(FieldValidator):

    def valid(self, value):
        return isinstance(value, datetime.datetime)

    def attempt_cast(self, value):
        if isinstance(value, str):
            return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
        elif isinstance(value, numbers.Integral) and not isinstance(value, bool):
            return datetime.datetime.utcfromtimestamp(value)
        else:
            raise errors.ValidationError('{0} failed to convert {1}, which is an unsupported type for datetime '
                                         'conversion. Please use a utc timestamp in seconds or a string with '
                                         'format %Y-%m-%dT%H:%M:%S'.format(self._field, value))

    def raise_validation_error(self, value):
        raise errors.ValidationError('{0} expects a date, got {1}'.format(self._field, value))


class BoolValidator(FieldValidator):

    def valid(self, value):
        return isinstance(value, bool)

    def attempt_cast(self, value):
        return bool(value)

    def raise_validation_error(self, value):
        raise errors.ValidationError('{0} expects True or False, got {1}'.format(self._field, value))


class ListValidator(FieldValidator):

    def valid(self, value):
        return isinstance(value, list)

    def attempt_cast(self, value):
        return list(value)

    def raise_validation_error(self, value):
        raise errors.ValidationError('{0} expects a list, got {1}'.format(self._field, value))

    def additional_validation(self, value):
        if self._field.item_type:
            for item in value:
                try:
                    self._field.item_type.set(item, cast=True)
                except errors.ValidationError as e:
                    raise errors.ValidationError('An item within {0} raised exception: {1}'.format(self._field, e))


class DictValidator(FieldValidator):

    def valid(self, value):
        return isinstance(value, dict)

    def attempt_cast(self, value):
        return dict(value)

    def raise_validation_error(self, value):
        raise errors.ValidationError('{0} expects a dict, got {1}'.format(self._field, value))


class NotSetMeta(type):
    def __repr__(self):
        return "Not Set"

    def __str__(self):
        return "Not Set"


class NotSet(object, metaclass=NotSetMeta):
    pass


class TypedField(object):
    validator_type = None

    def __init__(self, default=NotSet, notnull=False, readonly=False, *args, **kwargs):
        self.flags = {'notnull': notnull, 'readonly': readonly, 'default': default}
        self.name = 'noname'

        # a hook to allow subclasses to add their own unique parameters
        self.set_unique_attributes(**kwargs)

        # create validator
        self._validator = self._get_validator()
        self.flags['default'] = self._validator.validate(default, cast=False)
        self._value = self.flags['default']

    def __str__(self):
        return '{0}:{1}'.format(self.__class__.__name__, self.name)

    def set(self, value, cast=False):
        if value is NotSet:
            self._value = NotSet
        else:
            self._value = self._validator.validate(value, cast)
        return self._value

    def get(self):
        return self._value

    def validate(self, cast=False):
        return self._validator.validate(self._value, cast)

    def to_default(self):
        return self.set(self.flags['default'])

    def is_set(self):
        return self._value != NotSet and self._value != NotSetMeta

    def set_unique_attributes(self):
        pass

    def _get_validator(self):
        if self.validator_type:
            vt_cls = self.validator_type
            return vt_cls(self)
        else:
            raise NotImplementedError('Base class TypedField has no validator')


#Resource Fields
class ResourceField(TypedField):
    pass


class CharField(ResourceField):
    validator_type = CharValidator

    def set_unique_attributes(self, max_length=None):
        self.flags['max_length'] = max_length


class IntField(ResourceField):
    validator_type = IntValidator


class DecimalField(ResourceField):
    validator_type = DecimalValidator


class DateTimeField(ResourceField):
    validator_type = DateTimeValidator

    def set(self, value, cast=True):
        """
        DateTimeField defaults cast to True since serialized data won't be in a python datetime format.
        """
        return super().set(value, cast)


class BoolField(ResourceField):
    validator_type = BoolValidator


class ListField(ResourceField):
    validator_type = ListValidator

    def set_unique_attributes(self, item_type=NotSet):
        if item_type:
            if item_type == NotSet or not isinstance(item_type, ResourceField):
                raise errors.ValidationError('ListField must have an item_type set to a valid ResourceField')
            self.item_type = item_type
        else:
            self.item_type = None


class DictField(ResourceField):
    validator_type = DictValidator

#Resource Params


class ResourceParam(TypedField):
    pass


class CharParam(ResourceParam):
    validator_type = CharValidator

    def set_unique_attributes(self, max_length=None):
        self.flags['max_length'] = max_length


class IntParam(ResourceParam):
    validator_type = IntValidator


class DecimalParam(ResourceParam):
    validator_type = DecimalValidator


class DateTimeParam(ResourceParam):
    validator_type = DateTimeValidator

    def set(self, value, cast=True):
        """
        DateTimeParam defaults cast to True since serialized data won't be in a python datetime format.
        """
        return super().set(value, cast)


class BoolParam(ResourceParam):
    validator_type = BoolValidator


class ListParam(ResourceParam):
    validator_type = ListValidator

    def set(self, value, cast=False):
        if isinstance(value, str):
            value = value.split(',')
        return super().set(value, cast)

    def set_unique_attributes(self, item_type=None):
        if item_type:
            if item_type == NotSet or not isinstance(item_type, ResourceParam):
                raise errors.ValidationError('ListParam must have an item_type set to a valid ResourceParam')
            self.item_type = item_type
        else:
            self.item_type = None


