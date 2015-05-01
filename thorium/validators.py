# -*- coding: utf-8 -*-

import numbers
import datetime
import uuid
import json
import re

import jsonschema
import arrow

from . import errors, NotSet


class FieldValidator(object):

    def __init__(self, field):
        self._field = field

    def validate(self, value, cast=False):

        # NotSet is valid
        if value == NotSet:
            return NotSet

        # If value is None check whether field is nullable, if so raise an exception, if not return None
        if value is None:
            if self._field.flags['notnull']:
                raise errors.ValidationError('{0} cannot be null'.format(self._field))
            else:
                return None

        # Check the type of the value matches the type of the field
        value = self._type_validation(value, cast)

        self._validate_options(value)

        return value

    def valid(self, value):
        raise NotImplementedError()

    def attempt_cast(self, value):
        raise NotImplementedError()

    def raise_validation_error(self, value):
        raise NotImplementedError()

    def additional_validation(self, value):
        pass

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

    def _validate_options(self, value):
        if self._field.flags['options'] and value not in self._field.flags['options']:
            raise errors.ValidationError(
                '{field} value of {value} is not acceptable, must be one of: ({options})'.format(
                    field=self._field,
                    value=value,
                    options=', '.join([str(o) for o in self._field.flags['options']]))
            )


class CharValidator(FieldValidator):

    def valid(self, value):
        return isinstance(value, str)

    def attempt_cast(self, value):
        return str(value)

    def raise_validation_error(self, value):
        raise errors.ValidationError('{0} expects a string, got {1}'.format(self._field, value))

    def additional_validation(self, value):
        max_length = self._field.flags['max_length']
        if max_length and len(value) > max_length:
            err_msg = 'Max length of {0} is {1}, given value was {2}'.format(
                self._field,
                max_length,
                len(value),
            )
            raise errors.ValidationError(err_msg)
        regex = self._field.flags.get('regex')
        if regex and not regex.match(value):
            err_msg = '%s failed to match: %r' % (value, regex)
            raise errors.ValidationError(err_msg)


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


class DateValidator(FieldValidator):

    def valid(self, value):
        return isinstance(value, datetime.date)

    def attempt_cast(self, value):
        if isinstance(value, str):
            return datetime.datetime.strptime(value, "%Y-%m-%d").date()
        elif isinstance(value, numbers.Integral) and not isinstance(value, bool):
            return datetime.datetime.utcfromtimestamp(value).date()
        else:
            raise errors.ValidationError('{0} failed to convert {1}, which is an unsupported type for date '
                                         'conversion. Please use a string with '
                                         'format %Y-%m-%d'.format(self._field, value))

    def raise_validation_error(self, value):
        raise errors.ValidationError('{0} expects a date, got {1}'.format(self._field, value))


class DateTimeValidator(FieldValidator):

    def valid(self, value):
        return isinstance(value, datetime.datetime)

    def attempt_cast(self, value):
        if isinstance(value, str):
            try:
                return arrow.get(value).datetime.replace(tzinfo=None)
            except arrow.parser.ParserError as e:
                raise errors.ValidationError(
                    'Field {0}: {1}'.format(self._field, e)
                )
        elif isinstance(value, numbers.Number) and not isinstance(value, bool):
            return datetime.datetime.utcfromtimestamp(value)
        else:
            raise errors.ValidationError(
                '{0} failed to convert {1}, which is an unsupported type for '
                'datetime conversion. Please use a utc timestamp in seconds or'
                ' a string with format %Y-%m-%dT%H:%M:%S'
                .format(self._field, value))

    def raise_validation_error(self, value):
        error_msg = '{0} expects a date, got {1}'.format(self._field, value)
        raise errors.ValidationError(error_msg)


class TimeValidator(FieldValidator):

    def valid(self, value):
        return isinstance(value, datetime.time)

    def attempt_cast(self, value):
        if isinstance(value, str):
            try:
                return arrow.get(value, 'HH:mm:ss').time()
            except arrow.parser.ParserError as e:
                raise errors.ValidationError(
                    'Field {0}: {1}'.format(self._field, e)
                )
        else:
            raise errors.ValidationError(
                '{0} failed to convert {1}, which is an unsupported type for '
                'time conversion. Please use a'
                ' string with format HH:mm:ss'
                .format(self._field, value))

    def raise_validation_error(self, value):
        error_msg = '{0} expects a time, got {1}'.format(self._field, value)
        raise errors.ValidationError(error_msg)


class UUIDValidator(FieldValidator):

    def valid(self, value):
        return isinstance(value, uuid.UUID)

    def attempt_cast(self, value):
        if isinstance(value, str):
            return uuid.UUID(value)
        elif isinstance(value, bytes):
            return uuid.UUID(bytes=value)
        else:
            raise errors.ValidationError('Invalid type. Cannot cast to UUID.')

    def raise_validation_error(self, value):
        error_msg = '{0} expects a uuid, got {1}'.format(self._field, value)
        raise errors.ValidationError(error_msg)


class BoolValidator(FieldValidator):

    def valid(self, value):
        return isinstance(value, bool)

    def attempt_cast(self, value):
        if value in {True, 1, '1', 'true', 'True', 'TRUE'}:
            return True
        elif value in {False, 0, '0', 'false', 'False', 'FALSE'}:
            return False
        else:
            self.raise_validation_error(value)

    def raise_validation_error(self, value):
        raise errors.ValidationError('{0} expects True or False, got {1}'.format(self._field, value))


class ListValidator(FieldValidator):

    def valid(self, value):
        return isinstance(value, list)

    def attempt_cast(self, value):
        if isinstance(value, str):
            value = value.split(',')
        else:
            value = list(value)
        return value

    def raise_validation_error(self, value):
        raise errors.ValidationError('{0} expects a list, got {1}'.format(self._field, value))

    def additional_validation(self, value):
        item_type = self._field.flags['item_type']
        if item_type:
            for index, item in enumerate(value):
                try:
                    value[index] = item_type.validate(item, cast=True)  # Validates and casts list items
                except errors.ValidationError as e:
                    raise errors.ValidationError('An item within {0} raised exception: {1}'.format(self._field, e))

    def _validate_options(self, value):
        if self._field.flags['options']:
            if not set(value).issubset(set(self._field.flags['options'])):
                raise errors.ValidationError(
                    '{field} value of {value} is not acceptable, list items must be one of: ({options})'.format(
                        field=self._field,
                        value=value,
                        options=', '.join([str(o) for o in self._field.flags['options']]))
                )


class DictValidator(FieldValidator):

    def valid(self, value):
        return isinstance(value, dict)

    def attempt_cast(self, value):
        return dict(value)

    def raise_validation_error(self, value):
        raise errors.ValidationError('{0} expects a dict, got {1}'.format(self._field, value))


class SetValidator(FieldValidator):

    def valid(self, value):
        return isinstance(value, set)

    def attempt_cast(self, value):
        return set(value)

    def raise_validation_error(self, value):
        raise errors.ValidationError('{0} expects a set, got {1}'.format(self._field, value))

    def _validate_options(self, value):
        if self._field.flags['options']:
            if not value.issubset(set(self._field.flags['options'])):
                raise errors.ValidationError(
                    '{field} value of {value} is not acceptable, set items must be one of: ({options})'.format(
                        field=self._field,
                        value=value,
                        options=', '.join([str(o) for o in self._field.flags['options']]))
                )

class JSONValidator(FieldValidator):

    def valid(self, value):
        return isinstance(value, dict)

    def attempt_cast(self, value):
        return json.loads(value)

    def raise_validation_error(self, value):
        raise errors.ValidationError(
            '{0} contains invalid JSON'.format(self._field)
        )

    def additional_validation(self, value):
        if 'json_schema' in self._field.flags:
            try:
                jsonschema.validate(value, self._field.flags['json_schema'])
            except jsonschema.exceptions.ValidationError as err:
                raise errors.ValidationError(
                    '{0} contains malformed JSON: {1}'.format(
                        self._field,
                        str(err)
                    )
                )
