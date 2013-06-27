import calendar
import numbers
import datetime


#Field Validators
class FieldValidator(object):

    def __init__(self, field):
        self._field = field

    def validate(self, value, convert):
        if self._field.notnull and value is None:
            raise Exception('Value cannot be null')
        elif value is NotSet:
            return value
        elif value:
            value = self.type_validation(value, convert)

        return value

    def type_validation(self, value):
        raise NotImplementedError()


class CharValidator(FieldValidator):
    def type_validation(self, value, convert):
        if not isinstance(value, str):
            if convert:
                value = str(value)
            else:
                raise Exception('{0} is not a string.'.format(value))

        if self._field.max_length and len(value) > self._field.max_length:
            raise Exception('{0} exceeds max length of {1}'.format(value, self._field.max_length))
        return value


class IntValidator(FieldValidator):
    def type_validation(self, value, convert):
        if not isinstance(value, numbers.Integral):
            if convert:
                value = int(value)
            else:
                raise Exception('{0} is not an integer or long'.format(value))
        return value


class DecimalValidator(FieldValidator):
    def type_validation(self, value, convert):
        if not isinstance(value, numbers.Real):
            if convert:
                value = float(value)
            else:
                raise Exception('{0} is not a number'.format(value))
        return value


class DateTimeValidator(FieldValidator):
    def type_validation(self, value, convert):
        if not isinstance(value, datetime.datetime):
            if convert:
                value = datetime.datetime.fromtimestamp(int(value))
            else:
                raise Exception('{0} is not a date'.format(value))
        return value


class BoolValidator(FieldValidator):
    def type_validation(self, value, convert):
        if not isinstance(value, bool):
            if convert:
                value = bool(value)
            else:
                raise Exception('{0} is not a bool'.format(value))
        return value


class NotSet(object):
    pass


class TypedField(object):

    def __init__(self, default=NotSet, notnull=False, *args, **kwargs):

        # a hook to allow subclasses to add their own unique parameters
        self.set_unique_attributes(**kwargs)

        self.notnull = notnull

        # create validator
        self._validator = self.validator_type(self)

        self.default = self._validator.validate(default, convert=False)

        # set initial value to NotSet
        self._value = NotSet

    def set(self, value, convert=False):
        if value is NotSet:
            self._value = NotSet
        else:
            self._value = self._validator.validate(value, convert)
        return self._value

    def get(self):
        if self._value is NotSet:
            if self.default is NotSet:
                raise Exception('The value is not set and has no default.')
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
