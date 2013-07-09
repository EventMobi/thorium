import numbers
import datetime
from . import errors


#Field Validators
class FieldValidator(object):

    def __init__(self, field):
        self._field = field

    def validate(self, value):
        if self._field.notnull and value is None:
            raise errors.ValidationError('{0} cannot be null'.format(self._field))
        elif value is NotSet:
            return value
        elif value:
            value = self.type_validation(value)

        return value

    def type_validation(self, value):
        raise NotImplementedError()


class CharValidator(FieldValidator):
    def type_validation(self, value):
        if not isinstance(value, str):
            errors.ValidationError('{0} expects a string, got {1}'.format(self._field, value))

        if self._field.max_length and len(value) > self._field.max_length:
            raise errors.ValidationError('Max length of {0} is {1}, given value was {2}'.format(self._field, self._field.max_length, len(value)))
        return value


class IntValidator(FieldValidator):
    def type_validation(self, value):
        if not isinstance(value, numbers.Integral):
            raise errors.ValidationError('{0} expects an int or long, got {1}'.format(self._field, value))
        return value


class DecimalValidator(FieldValidator):
    def type_validation(self, value):
        if not isinstance(value, numbers.Real):
            raise errors.ValidationError('{0} expects a number, got {1}'.format(self._field, value))
        return value


class DateTimeValidator(FieldValidator):
    def type_validation(self, value):
        if not isinstance(value, datetime.datetime):
            try:
                if isinstance(value, str):
                    value = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
                else:
                    value = datetime.datetime.fromtimestamp(int(value))
            except:
                raise errors.ValidationError('{0} expects a date, got {1}'.format(self._field, value))
        return value


class BoolValidator(FieldValidator):
    def type_validation(self, value):
        if not isinstance(value, bool):
            raise errors.ValidationError('{0} expects True or False, got {1}'.format(self._field, value))
        return value


class NotSet(object):
    pass


class TypedField(object):

    def __init__(self, default=NotSet, notnull=False, *args, **kwargs):
        self.name = 'noname'

        # a hook to allow subclasses to add their own unique parameters
        self.set_unique_attributes(**kwargs)

        self.notnull = notnull

        # create validator
        self._validator = self.validator_type(self)

        self.default = self._validator.validate(default)

        # set initial value to NotSet
        self._value = NotSet

    def __str__(self):
        return '{0}:{1}'.format(self.__class__.__name__, self.name)

    def set(self, value):
        if value is NotSet:
            self._value = NotSet
        else:
            self._value = self._validator.validate(value)
        return self._value

    def get(self):
        if self._value is NotSet:
            if self.default is NotSet:
                raise errors.ValidationError('The value of {0} is not set and has no default.'.format(self))
            else:
                return self.default
        return self._value

    def to_default(self):
        return self.set(self.default)

    def is_set(self):
        return self._value != NotSet

    def set_unique_attributes(self, max_length=None):
        pass


#Resource Fields
class ResourceField(TypedField):
    pass


class CharField(ResourceField):
    validator_type = CharValidator

    def set_unique_attributes(self, max_length=None):
        self.max_length = max_length


class IntField(ResourceField):
    validator_type = IntValidator


class DecimalField(ResourceField):
    validator_type = DecimalValidator


class DateTimeField(ResourceField):
    validator_type = DateTimeValidator


class BoolField(ResourceField):
    validator_type = BoolValidator


#Resource Params
class ResourceParam(TypedField):
    pass


class CharParam(ResourceParam):
    validator_type = CharValidator

    def set_unique_attributes(self, max_length=None):
        self.max_length = max_length


class IntParam(ResourceParam):
    validator_type = IntValidator


class DecimalParam(ResourceParam):
    validator_type = DecimalValidator


class DateTimeParam(ResourceParam):
    validator_type = DateTimeValidator


class BoolParam(ResourceParam):
    validator_type = BoolValidator
