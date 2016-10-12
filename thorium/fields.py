# -*- coding: utf-8 -*-

import re

from . import errors, validators, NotSet


class ResourceField(object):
    validator_type = None
    order_counter = 0

    def __init__(self, default=NotSet, notnull=False, readonly=False,
                 writeonly=False, options=None, cast=None, required=False,
                 immutable=False, detail=False, *args, **kwargs):
        self.flags = {
            'notnull': notnull,
            'readonly': readonly,
            'default': default,
            'writeonly': writeonly,
            'options': options,
            'cast': cast,
            'required': required,
            'immutable': immutable,
            'detail': detail,
        }

        self.name = 'noname'

        self.order_value = ResourceField.order_counter
        ResourceField.order_counter += 1

        # a hook to allow subclasses to add their own unique parameters
        self.set_unique_attributes(**kwargs)

        # create validator
        self._validator = self._get_validator()
        if callable(default):
            self.flags['default'] = default
        else:
            self.flags['default'] = self._validator.validate(default, cast=False)

    def __str__(self):
        return '{0}:{1}'.format(self.__class__.__name__, self.name)

    def validate(self, value, cast=False):
        cast = self.flags['cast'] if self.flags['cast'] is not None else cast
        return self._validator.validate(value, cast)

    @property
    def is_readonly(self):
        return self.flags['readonly']

    @property
    def is_immutable(self):
        return self.flags['immutable']

    @property
    def is_required(self):
        return self.flags['required']

    @property
    def default(self):
        return self.flags['default']

    @property
    def detail(self):
        return self.flags['detail']

    def set_unique_attributes(self, **kwargs):
        for key, value in kwargs.items():
            self.flags[key] = value

    def _get_validator(self):
        if self.validator_type:
            vt_cls = self.validator_type
            return vt_cls(self)
        else:
            raise NotImplementedError('Base class ResourceField has no validator')


class CharField(ResourceField):
    validator_type = validators.CharValidator

    def set_unique_attributes(self, max_length=None, regex=None):
        self.flags['max_length'] = max_length
        self.flags['regex'] = re.compile(regex) if regex else regex


class IntField(ResourceField):
    validator_type = validators.IntValidator


class DecimalField(ResourceField):
    validator_type = validators.DecimalValidator


class DateField(ResourceField):
    validator_type = validators.DateValidator

    # default cast to True
    def __init__(self, *args, cast=True, **kwargs):
        super().__init__(*args, cast=cast, **kwargs)


class DateTimeField(ResourceField):
    validator_type = validators.DateTimeValidator

    # default cast to True
    def __init__(self, *args, cast=True, **kwargs):
        super().__init__(*args, cast=cast, **kwargs)


class TimeField(ResourceField):
    validator_type = validators.TimeValidator

    # default cast to True
    def __init__(self, *args, cast=True, **kwargs):
        super().__init__(*args, cast=cast, **kwargs)


class UUIDField(ResourceField):
    validator_type = validators.UUIDValidator

    # default cast to True
    def __init__(self, *args, cast=True, **kwargs):
        super().__init__(*args, cast=cast, **kwargs)


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


class JSONField(ResourceField):
    validator_type = validators.JSONValidator

    def set_unique_attributes(self, schema=None):
        if schema:
            self.flags['json_schema'] = schema
