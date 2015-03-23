# -*- coding: utf-8 -*-

import datetime
import types
import uuid

from unittest import TestCase, mock

from thorium import fields, params, errors, NotSet, validators


class TestNotSet(TestCase):

    def setUp(self):
        self.field = NotSet

    def test_notset_is_equal_to_notset(self):
        self.assertEqual(self.field, NotSet)
        self.assertEqual(NotSet, NotSet)

    def test_notset_is_not_none(self):
        self.assertNotEqual(NotSet, None)

    def test_notset_is_not_false(self):
        self.assertNotEqual(NotSet, False)

    def test_notset_is_not_true(self):
        self.assertNotEqual(NotSet, True)

    def test_notset_is_falsey(self):
        self.assertEqual(bool(NotSet), False)
        if self.field:
            self.fail('Notset should be falsey')
        hit = False
        if not self.field:
            hit = True
        self.assertTrue(hit)


class TestExtraFlags(TestCase):

    def setUp(self):
        self.extra = {
            'extra_bool': True,
            'extra_str': 'Yes',
            'extra_int': 100
        }
        self.field = fields.IntField(default=99, **self.extra)

    def test_extra_flags(self):
        self.assertEqual(self.field.flags['extra_bool'],
                         self.extra['extra_bool'])
        self.assertEqual(self.field.flags['extra_str'],
                         self.extra['extra_str'])
        self.assertEqual(self.field.flags['extra_int'],
                         self.extra['extra_int'])


class TestFieldValidator(TestCase):

    def setUp(self):
        self._field = mock.MagicMock()
        self._field.flags = {'notnull': True}
        self.validator = validators.FieldValidator(self._field)

    def test_validate(self):
        self.assertRaises(NotImplementedError, self.validator.validate, 10)

    def test_validate_notnull(self):
        self.assertRaises(errors.ValidationError, self.validator.validate,
                          None)

    def test_validate_not_set(self):
        self.assertEqual(self.validator.validate(NotSet), NotSet)

    def test_validate_with_nullable_field(self):
        self._field.flags = {'notnull': False}
        validator_nullable = validators.FieldValidator(self._field)
        self.assertEqual(validator_nullable.validate(None), None)

    def test_validate_returns_value(self):
        def func(self, value):
            return value

        self.validator.validate = types.MethodType(func, self.validator)
        self.assertEqual(self.validator.validate(True), True)
        self.assertEqual(self.validator.validate(False), False)
        self.assertEqual(self.validator.validate(10), 10)


class TestCharValidator(TestCase):

    def setUp(self):
        self.char_field = mock.MagicMock(fields.CharField)
        self.char_field.flags = {
            'max_length': 10,
            'notnull': True,
            'options': None
        }
        self.validator = validators.CharValidator(self.char_field)

    def test_validate(self):
        result = self.validator.validate('test1')
        self.assertEqual('test1', result)

    def test_int_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.validate, 1)

    def test_bool_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.validate,
                          True)

    def test_date_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.validate,
                          datetime.datetime)

    def test_max_length(self):
        self.assertRaises(errors.ValidationError, self.validator.validate,
                          'longer than 10 characters')


class TestIntValidator(TestCase):

    def setUp(self):
        self._field = mock.MagicMock(fields.IntField)
        self._field.flags = {'options': None}
        self.validator = validators.IntValidator(self._field)

    def test_validate(self):
        result = self.validator.validate(42)
        self.assertEqual(42, result)

    def test_long_validation(self):
        result = self.validator.validate(420000000000000000000000000)
        self.assertEqual(420000000000000000000000000, result)

    def test_str_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.validate,
                          'abc')

    def test_bool_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.validate,
                          True)

    def test_date_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.validate,
                          datetime.datetime)


class TestDateValidator(TestCase):

    def setUp(self):
        self._field = mock.MagicMock(fields.DateField)
        self._field.flags = {'options': None}
        self.validator = validators.DateValidator(self._field)

    def test_validate(self):
        dt = datetime.date.today()
        result = self.validator.validate(dt)
        self.assertEqual(dt, result)

    def test_str_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.validate,
                          'abc')

    def test_bool_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.validate,
                          True)

    def test_int_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.validate, 1)


class TestDateTimeValidator(TestCase):

    def setUp(self):
        self._field = mock.MagicMock(fields.DateTimeField)
        self._field.flags = {'options': None}
        self.validator = validators.DateTimeValidator(self._field)

    def test_validate(self):
        dt = datetime.datetime.utcnow()
        result = self.validator.validate(dt)
        self.assertEqual(dt, result)

    def test_isoformated_date_to_datetime(self):
        dt = datetime.datetime(2015, 3, 2)
        result = self.validator.validate('2015-03-02', cast=True)
        self.assertEqual(dt, result)

    def test_isoformated_datetime_to_datetime(self):
        dt = datetime.datetime(2015, 3, 2, hour=14, minute=41, second=53)
        result = self.validator.validate('2015-03-02T14:41:53', cast=True)
        self.assertEqual(dt, result)

    def test_isoformated_datetime_with_microseconds_to_datetime(self):
        dt = datetime.datetime(2015, 3, 2, hour=14, minute=41, second=53,
                               microsecond=834910)
        result = self.validator.validate('2015-03-02T14:41:53.834910',
                                         cast=True)
        self.assertEqual(dt, result)

    def test_str_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.validate,
                          'abc')

    def test_bool_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.validate,
                          True)

    def test_int_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.validate, 1)

    def test_invalid_isoformated_datetime(self):
        self.assertRaises(errors.ValidationError, self.validator.validate,
                          '2015-03-02Z14:41:53.834910')


class TestUUIDValidator(TestCase):

    def setUp(self):
        self._field = mock.MagicMock(fields.UUIDField)
        self._field.flags = {'options': None}
        self.validator = validators.UUIDValidator(self._field)

    def test_validate(self):
        test_uuid = uuid.uuid4()
        self.assertEqual(test_uuid, self.validator.validate(test_uuid))
        uuid_str = '53be3a61-2eac-497e-88aa-5e938413b111'
        self.assertEqual(uuid.UUID(uuid_str),
                         self.validator.validate(uuid_str, cast=True))
        uuid_b = b'\xfb\x10\x0b\xe6\x83\xbdC\xcd\xbe\x81\xc7\xf2\xf8\xe2J\x05'
        self.assertEqual(uuid.UUID(bytes=uuid_b),
                         self.validator.validate(uuid_b, cast=True))

    def test_invalid_str(self):
        self.assertRaises(ValueError,
                          lambda: self.validator.attempt_cast('foo'))

    def test_invalid_bytes(self):
        self.assertRaises(ValueError,
                          lambda: self.validator.attempt_cast(
                              b'12345678901234567'
                          ))


class TestDecimalValidator(TestCase):

    def setUp(self):
        self._field = mock.MagicMock(fields.DecimalField)
        self._field.flags = {'options': None}
        self.validator = validators.DecimalValidator(self._field)

    def test_validate(self):
        result = self.validator.validate(4.2)
        self.assertEqual(4.2, result)

    def test_str_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.validate,
                          'abc')

    def test_bool_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.validate,
                          True)

    def test_date_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.validate,
                          datetime.datetime)


class TestBoolValidator(TestCase):

    def setUp(self):
        self.field_mock = mock.MagicMock()
        self.field_mock.flags = {'options': None}
        self.validator = validators.BoolValidator(self.field_mock)

    def test_validate(self):
        result = self.validator.validate(True)
        self.assertEqual(result, True)
        result = self.validator.validate(False)
        self.assertEqual(result, False)

    def test_str_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.validate,
                          'abc')

    def test_int_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.validate, 92)

    def test_date_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.validate,
                          datetime.datetime)

    def test_cast(self):
        self.assertTrue(self.validator.validate(True, cast=True))
        self.assertTrue(self.validator.validate(1, cast=True))
        self.assertTrue(self.validator.validate('1', cast=True))
        self.assertTrue(self.validator.validate('true', cast=True))
        self.assertTrue(self.validator.validate('True', cast=True))
        self.assertTrue(self.validator.validate('TRUE', cast=True))
        self.assertFalse(self.validator.validate(False, cast=True))
        self.assertFalse(self.validator.validate(0, cast=True))
        self.assertFalse(self.validator.validate('0', cast=True))
        self.assertFalse(self.validator.validate('false', cast=True))
        self.assertFalse(self.validator.validate('False', cast=True))
        self.assertFalse(self.validator.validate('FALSE', cast=True))
        self.assertRaises(errors.ValidationError, self.validator.validate, 2,
                          True)
        self.assertRaises(errors.ValidationError, self.validator.validate,
                          'tRuE', True)
        self.assertRaises(errors.ValidationError, self.validator.validate, -1,
                          True)


class TestListValidator(TestCase):

    def setUp(self):
        self.list_field = mock.MagicMock(fields.ListField)
        self.list_field.flags = {
            'item_type': fields.IntField(),
            'notnull': True,
            'options': None,
        }
        self.validator = validators.ListValidator(self.list_field)

    def test_validate(self):
        self.assertEqual(self.validator.validate([]), [])
        self.assertTrue(self.validator.validate([5, 3, 1]))
        self.assertTrue(self.validator.validate(['1', '2', '3']))

    def test_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.validate,
                          'abc')
        self.assertRaises(errors.ValidationError, self.validator.validate,
                          ['1', 'abc'])
        self.assertRaises(errors.ValidationError, self.validator.validate,
                          '1,2,3,4')

    def test_cast(self):
        self.assertTrue(self.validator.validate((1, 2, 3), cast=True))
        self.assertRaises(errors.ValidationError, self.validator.validate,
                          (1, 2, 3), False)


class SimpleValidator(validators.FieldValidator):

    def validate(self, value, cast=False):
        return value


class SimpleResourceField(fields.ResourceField):
        validator_type = SimpleValidator


class TestResourceField(TestCase):

    def setUp(self):
        self.field = SimpleResourceField()

    def test_init(self):
        self.assertRaises(NotImplementedError, fields.ResourceField)

        simple = SimpleResourceField()
        self.assertEqual(simple.name, 'noname')
        self.assertEqual(simple.flags['notnull'], False)
        self.assertEqual(simple.flags['default'], NotSet)
        self.assertEqual(simple.flags['readonly'], False)

        with_default = SimpleResourceField(default=10)
        self.assertEqual(with_default.flags['notnull'], False)
        self.assertEqual(with_default.flags['default'], 10)
        self.assertEqual(with_default.flags['readonly'], False)

        with_notnull = SimpleResourceField(notnull=True)
        self.assertEqual(with_notnull.flags['notnull'], True)
        self.assertEqual(with_notnull.flags['default'], NotSet)
        self.assertEqual(with_default.flags['readonly'], False)

        with_default = SimpleResourceField(readonly=True)
        self.assertEqual(with_default.flags['notnull'], False)
        self.assertEqual(with_default.flags['default'], NotSet)
        self.assertEqual(with_default.flags['readonly'], True)

    def test_validate_with_notset(self):
        self.assertEqual(self.field.validate(NotSet), NotSet)

    def test_validate_with_value(self):
        self.assertEqual(self.field.validate(10), 10)

    def test_set_unique_attributes(self):
        self.field.set_unique_attributes()

    def test_get_validator(self):
        v = self.field._get_validator()
        self.assertTrue(isinstance(v, SimpleValidator))

        self.field.validator_type = None
        self.assertRaises(NotImplementedError, self.field._get_validator)


class TestCharField(TestCase):

    def setUp(self):
        self.field = fields.CharField()

    def test_inheritance(self):
        self.assertTrue(isinstance(self.field, fields.ResourceField))

    def test_validator_type(self):
        self.assertEqual(self.field.validator_type, validators.CharValidator)

    def test_set_unique_attributes(self):
        self.assertEqual(self.field.flags['max_length'], None)
        self.field.set_unique_attributes(max_length=99)
        self.assertEqual(self.field.flags['max_length'], 99)

    def test_field_usage(self):
        self.assertEqual(self.field.validate('hello world!'), 'hello world!')

    def test_field_maxlength(self):
        self.field.flags['max_length'] = 5
        self.assertRaises(errors.ValidationError, self.field.validate,
                          'too long for max_length')

    def test_field_invalid_values(self):
        self.assertRaises(errors.ValidationError, self.field.validate, 10)
        self.assertRaises(errors.ValidationError, self.field.validate,
                          datetime.datetime.utcnow())
        self.assertRaises(errors.ValidationError, self.field.validate, True)

    def test_field_options(self):
        self.field.flags['options'] = {'a', 'b', 1, 2}
        self.assertEqual(self.field.validate('a'), 'a')
        self.assertEqual(self.field.validate('b'), 'b')
        self.assertEqual(self.field.validate(None), None)
        self.assertEqual(self.field.validate(NotSet), NotSet)
        self.assertRaises(errors.ValidationError, self.field.validate, 'c')
        self.assertRaises(errors.ValidationError, self.field.validate, 'd')
        self.assertRaises(errors.ValidationError, self.field.validate, 1)
        self.assertRaises(errors.ValidationError, self.field.validate, 2)
        self.field.flags['options'] = ['a', 'b', 1, 2]
        self.assertEqual(self.field.validate('a'), 'a')
        self.assertEqual(self.field.validate('b'), 'b')
        self.assertEqual(self.field.validate(None), None)
        self.assertEqual(self.field.validate(NotSet), NotSet)
        self.assertRaises(errors.ValidationError, self.field.validate, 'c')
        self.assertRaises(errors.ValidationError, self.field.validate, 'd')
        self.assertRaises(errors.ValidationError, self.field.validate, 1)
        self.assertRaises(errors.ValidationError, self.field.validate, 2)


class TestIntField(TestCase):

    def setUp(self):
        self.field = fields.IntField()

    def test_inheritance(self):
        self.assertTrue(isinstance(self.field, fields.ResourceField))

    def test_validator_type(self):
        self.assertEqual(self.field.validator_type, validators.IntValidator)

    def test_field_usage(self):
        self.assertEqual(self.field.validate(10), 10)

    def test_field_invalid_values(self):
        self.assertRaises(errors.ValidationError, self.field.validate, 'abc')
        self.assertRaises(errors.ValidationError, self.field.validate,
                          datetime.datetime.utcnow())
        self.assertRaises(errors.ValidationError, self.field.validate, True)

    def test_field_options(self):
        self.field.flags['options'] = {'a', 'b', 1, 2}
        self.assertEqual(self.field.validate(1), 1)
        self.assertEqual(self.field.validate(2), 2)
        self.assertEqual(self.field.validate(None), None)
        self.assertEqual(self.field.validate(NotSet), NotSet)
        self.assertRaises(errors.ValidationError, self.field.validate, 'c')
        self.assertRaises(errors.ValidationError, self.field.validate, 'd')
        self.assertRaises(errors.ValidationError, self.field.validate, 3)
        self.assertRaises(errors.ValidationError, self.field.validate, 4)
        self.field.flags['options'] = ['a', 'b', 1, 2]
        self.assertEqual(self.field.validate(1), 1)
        self.assertEqual(self.field.validate(2), 2)
        self.assertEqual(self.field.validate(None), None)
        self.assertEqual(self.field.validate(NotSet), NotSet)
        self.assertRaises(errors.ValidationError, self.field.validate, 'c')
        self.assertRaises(errors.ValidationError, self.field.validate, 'd')
        self.assertRaises(errors.ValidationError, self.field.validate, 3)
        self.assertRaises(errors.ValidationError, self.field.validate, 4)


class TestBoolField(TestCase):

    def setUp(self):
        self.field = fields.BoolField()

    def test_inheritance(self):
        self.assertTrue(isinstance(self.field, fields.ResourceField))

    def test_validator_type(self):
        self.assertEqual(self.field.validator_type, validators.BoolValidator)

    def test_field_usage(self):
        self.assertEqual(self.field.validate(True), True)

    def test_field_invalid_values(self):
        self.assertRaises(errors.ValidationError, self.field.validate, 'abc')
        self.assertRaises(errors.ValidationError, self.field.validate,
                          datetime.datetime.utcnow())
        self.assertRaises(errors.ValidationError, self.field.validate, 10)

    def test_field_options(self):
        self.field.flags['options'] = {'a', 'b', False}
        self.assertEqual(self.field.validate(False), False)
        self.assertEqual(self.field.validate(None), None)
        self.assertEqual(self.field.validate(NotSet), NotSet)
        self.assertRaises(errors.ValidationError, self.field.validate, 'c')
        self.assertRaises(errors.ValidationError, self.field.validate, 'd')
        self.assertRaises(errors.ValidationError, self.field.validate, True)
        self.assertRaises(errors.ValidationError, self.field.validate, 0)
        self.assertRaises(errors.ValidationError, self.field.validate, 1)
        self.field.flags['options'] = ['a', 'b', 1, False]
        # True in {1} returns True
        self.assertEqual(self.field.validate(True), True)
        self.assertEqual(self.field.validate(False), False)
        self.assertEqual(self.field.validate(None), None)
        self.assertEqual(self.field.validate(NotSet), NotSet)
        self.assertRaises(errors.ValidationError, self.field.validate, 'c')
        self.assertRaises(errors.ValidationError, self.field.validate, 'd')
        self.assertRaises(errors.ValidationError, self.field.validate, 0)


class TestDecimalField(TestCase):

    def setUp(self):
        self.field = fields.DecimalField()

    def test_inheritance(self):
        self.assertTrue(isinstance(self.field, fields.ResourceField))

    def test_validator_type(self):
        self.assertEqual(self.field.validator_type,
                         validators.DecimalValidator)

    def test_field_usage(self):
        self.assertEqual(self.field.validate(5.234), 5.234)

    def test_field_invalid_values(self):
        self.assertRaises(errors.ValidationError, self.field.validate, 'abc')
        self.assertRaises(errors.ValidationError, self.field.validate,
                          datetime.datetime.utcnow())
        self.assertRaises(errors.ValidationError, self.field.validate, True)

    def test_field_options(self):
        self.field.flags['options'] = {'a', 'b', 1.3, 2.4}
        self.assertEqual(self.field.validate(1.3), 1.3)
        self.assertEqual(self.field.validate(2.4), 2.4)
        self.assertEqual(self.field.validate(None), None)
        self.assertEqual(self.field.validate(NotSet), NotSet)
        self.assertRaises(errors.ValidationError, self.field.validate, 'c')
        self.assertRaises(errors.ValidationError, self.field.validate, 'd')
        self.assertRaises(errors.ValidationError, self.field.validate, 3)
        self.assertRaises(errors.ValidationError, self.field.validate, 4)
        self.assertRaises(errors.ValidationError, self.field.validate, 2.44)
        self.assertRaises(errors.ValidationError, self.field.validate, 2)
        self.field.flags['options'] = ['a', 'b', 1.3, 2.4]
        self.assertEqual(self.field.validate(1.3), 1.3)
        self.assertEqual(self.field.validate(2.4), 2.4)
        self.assertEqual(self.field.validate(None), None)
        self.assertEqual(self.field.validate(NotSet), NotSet)
        self.assertRaises(errors.ValidationError, self.field.validate, 'a')
        self.assertRaises(errors.ValidationError, self.field.validate, 'b')
        self.assertRaises(errors.ValidationError, self.field.validate, 3)
        self.assertRaises(errors.ValidationError, self.field.validate, 4)
        self.assertRaises(errors.ValidationError, self.field.validate, 2.44)
        self.assertRaises(errors.ValidationError, self.field.validate, 2)


class TestDateField(TestCase):

    def setUp(self):
        self.field = fields.DateField()

    def test_inheritance(self):
        self.assertTrue(isinstance(self.field, fields.ResourceField))

    def test_validator_type(self):
        self.assertEqual(self.field.validator_type, validators.DateValidator)

    def test_field_usage(self):
        self.assertEqual(self.field.validate(datetime.date.today()),
                         datetime.date.today())

    def test_field_invalid_values(self):
        self.assertRaises(errors.ValidationError, self.field.validate, 'abc')
        self.assertRaises(errors.ValidationError, self.field.validate, True)

    def test_field_options(self):
        dt = datetime.date(2011, 10, 12)
        self.field.flags['options'] = {'a', 3435, dt}
        self.assertEqual(self.field.validate(dt), dt)
        self.assertEqual(self.field.validate(None), None)
        self.assertEqual(self.field.validate(NotSet), NotSet)
        self.assertRaises(errors.ValidationError, self.field.validate,
                          datetime.date.today())
        self.assertRaises(errors.ValidationError, self.field.validate, 'a')
        self.assertRaises(errors.ValidationError, self.field.validate, 3435)


class TestDateTimeField(TestCase):

    def setUp(self):
        self.field = fields.DateTimeField()

    def test_inheritance(self):
        self.assertTrue(isinstance(self.field, fields.ResourceField))

    def test_validator_type(self):
        self.assertEqual(self.field.validator_type,
                         validators.DateTimeValidator)

    def test_field_usage(self):
        dt = datetime.datetime.utcnow()
        self.assertEqual(self.field.validate(dt), dt)

    def test_field_invalid_values(self):
        self.assertRaises(errors.ValidationError, self.field.validate, 'abc')
        self.assertRaises(errors.ValidationError, self.field.validate, True)

    def test_field_options(self):
        dt = datetime.datetime(2011, 10, 12)
        self.field.flags['options'] = {'a', 3435, dt}
        self.assertEqual(self.field.validate(dt), dt)
        self.assertEqual(self.field.validate(None), None)
        self.assertEqual(self.field.validate(NotSet), NotSet)
        self.assertRaises(errors.ValidationError, self.field.validate,
                          datetime.datetime.utcnow())
        self.assertRaises(errors.ValidationError, self.field.validate, 'a')
        self.assertRaises(errors.ValidationError, self.field.validate, 3435)


class TestListField(TestCase):

    def setUp(self):
        self.field = fields.ListField()

    def test_inheritance(self):
        self.assertTrue(isinstance(self.field, fields.ResourceField))

    def test_validator_type(self):
        self.assertEqual(self.field.validator_type, validators.ListValidator)

    def test_field_usage(self):
        self.assertEqual(self.field.validate([]), [])
        self.assertEqual(self.field.validate([1, 2, 3]), [1, 2, 3])
        self.assertEqual(self.field.validate(['1', '2', '3']), ['1', '2', '3'])
        self.assertEqual(self.field.validate((), cast=True), [])
        self.assertEqual(self.field.validate((1, 2, 3), cast=True), [1, 2, 3])
        self.assertEqual(self.field.validate(('1', '2', '3'), cast=True),
                         ['1', '2', '3'])

    def test_field_invalid_values(self):
        self.assertRaises(errors.ValidationError, self.field.validate, 4)
        self.assertRaises(errors.ValidationError, self.field.validate, ())
        self.assertRaises(errors.ValidationError, self.field.validate,
                          (1, 2, 3))

    def test_field_list_item_type_int(self):
        self.assertRaises(errors.ValidationError, fields.ListField,
                          item_type=params.IntParam())
        field = fields.ListField(item_type=fields.IntField())
        self.assertEqual(field.validate([]), [])
        self.assertEqual(field.validate([1, 2, 3]), [1, 2, 3])
        self.assertEqual(field.validate(['1', '2', '3']), [1, 2, 3])
        self.assertEqual(field.validate((), cast=True), [])
        self.assertEqual(field.validate((1, 2, 3), cast=True), [1, 2, 3])
        self.assertEqual(field.validate(('1', '2', '3'), cast=True), [1, 2, 3])
        self.assertEqual(field.validate('1,2,3', cast=True), [1, 2, 3])
        self.assertRaises(errors.ValidationError, field.validate, 'abc')
        self.assertRaises(errors.ValidationError, field.validate,
                          ['abc', 'efd'])
        self.assertRaises(errors.ValidationError, field.validate, ())
        self.assertRaises(errors.ValidationError, field.validate, (1, 2, 3))

    def test_field_list_item_type_char(self):
        self.assertRaises(errors.ValidationError, fields.ListField,
                          item_type=params.CharParam())
        field = fields.ListField(item_type=fields.CharField())
        self.assertEqual(field.validate([]), [])
        self.assertEqual(field.validate(['1', '2', '3']), ['1', '2', '3'])
        self.assertEqual(field.validate([1, 2, 3]), ['1', '2', '3'])
        self.assertEqual(field.validate((), cast=True), [])
        self.assertEqual(field.validate(('1', '2', '3'), cast=True),
                         ['1', '2', '3'])
        self.assertEqual(field.validate((1, 2, 3), cast=True), ['1', '2', '3'])
        self.assertEqual(field.validate('1,2,3', cast=True), ['1', '2', '3'])
        self.assertRaises(errors.ValidationError, field.validate, ())
        self.assertRaises(errors.ValidationError, field.validate, (1, 2, 3))

    def test_field_list_item_type_bool(self):
        self.assertRaises(errors.ValidationError, fields.ListField,
                          item_type=params.BoolParam())
        field = fields.ListField(item_type=fields.BoolField())
        self.assertEqual(field.validate([]), [])
        self.assertEqual(field.validate([True, False, 1, 0]),
                         [True, False, True, False])
        self.assertEqual(field.validate(['0', '1']), [False, True])
        self.assertEqual(field.validate([0, 1]), [False, True])
        self.assertEqual(field.validate((), cast=True), [])
        self.assertEqual(field.validate((True, False, 1, 0), cast=True),
                         [True, False, True, False])
        self.assertEqual(field.validate(('0', '1'), cast=True), [False, True])
        self.assertEqual(field.validate((0, 1), cast=True), [False, True])
        self.assertRaises(errors.ValidationError, field.validate,
                          ['abc', 'edf'])
        self.assertRaises(errors.ValidationError, field.validate, [2])
        self.assertRaises(errors.ValidationError, field.validate, ())
        self.assertRaises(errors.ValidationError, field.validate, (1, 2, 3))

    def test_field_list_item_type_decimal(self):
        self.assertRaises(errors.ValidationError, fields.ListField,
                          item_type=params.DecimalParam())
        field = fields.ListField(item_type=fields.DecimalField())
        self.assertEqual(field.validate([]), [])
        self.assertEqual(field.validate([0, 1, 1.123, -123]),
                         [0, 1, 1.123, -123])
        self.assertEqual(field.validate(['0.123', '1']), [0.123, 1])
        self.assertEqual(field.validate([True, False]), [1, 0])
        self.assertEqual(field.validate((), cast=True), [])
        self.assertEqual(field.validate((0, 1, 1.123, -123), cast=True),
                         [0, 1, 1.123, -123])
        self.assertEqual(field.validate(('0.123', '1'), cast=True), [0.123, 1])
        self.assertRaises(errors.ValidationError, field.validate,
                          ['abc', 'edf'])
        self.assertRaises(errors.ValidationError, field.validate, ())
        self.assertRaises(errors.ValidationError, field.validate, (1, 2, 3))

    def test_field_list_item_type_datetime(self):
        pass

    def test_field_list_item_type_list(self):
        self.assertRaises(errors.ValidationError, fields.ListField,
                          item_type=params.ListParam())
        field = fields.ListField(
            item_type=fields.ListField(item_type=fields.IntField())
        )
        self.assertEqual(field.validate([]), [])
        self.assertEqual(field.validate([[1, 2, 3], [True, False], [1.2]]),
                         [[1, 2, 3], [1, 0], [1]])
        self.assertRaises(errors.ValidationError, field.validate,
                          [[1, 2, 3], 4, [1.2]])

    def test_field_list_item_type_dict(self):
        pass

    def test_field_options(self):
        self.field.flags['options'] = ['a', 3, 1, 2, 'b']
        self.assertEqual(self.field.validate([1, 2]), [1, 2])
        self.assertEqual(self.field.validate(['a']), ['a'])
        self.assertEqual(self.field.validate(['a', 'b']), ['a', 'b'])
        self.assertEqual(self.field.validate(None), None)
        self.assertEqual(self.field.validate(NotSet), NotSet)
        self.assertEqual(self.field.validate([]), [])
        self.assertRaises(errors.ValidationError, self.field.validate, 'a')
        self.assertRaises(errors.ValidationError, self.field.validate, 3)
        self.assertRaises(
            errors.ValidationError, self.field.validate, ['a', 'b', 'c']
        )


class TestCharParam(TestCase):

    def setUp(self):
        self.field = params.CharParam()

    def test_inheritance(self):
        self.assertTrue(isinstance(self.field, params.ResourceParam))

    def test_validator_type(self):
        self.assertEqual(self.field.validator_type, validators.CharValidator)

    def test_set_unique_attributes(self):
        self.assertEqual(self.field.flags['max_length'], None)
        self.field.set_unique_attributes(max_length=99)
        self.assertEqual(self.field.flags['max_length'], 99)

    def test_param_usage(self):
        self.assertEqual(self.field.validate('hello world!'), 'hello world!')

    def test_param_maxlength(self):
        self.field.flags['max_length'] = 5
        self.assertRaises(errors.ValidationError, self.field.validate,
                          'too long for max_length')

    def test_param_invalid_values(self):
        self.assertRaises(errors.ValidationError, self.field.validate, 10)
        self.assertRaises(errors.ValidationError, self.field.validate,
                          datetime.datetime.utcnow())
        self.assertRaises(errors.ValidationError, self.field.validate, True)

    def test_param_options(self):
        self.field.flags['options'] = {'a', 'b', 1, 2}
        self.assertEqual(self.field.validate('a'), 'a')
        self.assertEqual(self.field.validate('b'), 'b')
        self.assertEqual(self.field.validate(None), None)
        self.assertEqual(self.field.validate(NotSet), NotSet)
        self.assertRaises(errors.ValidationError, self.field.validate, 'c')
        self.assertRaises(errors.ValidationError, self.field.validate, 'd')
        self.assertRaises(errors.ValidationError, self.field.validate, 1)
        self.assertRaises(errors.ValidationError, self.field.validate, 2)
        self.field.flags['options'] = ['a', 'b', 1, 2]
        self.assertEqual(self.field.validate('a'), 'a')
        self.assertEqual(self.field.validate('b'), 'b')
        self.assertEqual(self.field.validate(None), None)
        self.assertEqual(self.field.validate(NotSet), NotSet)
        self.assertRaises(errors.ValidationError, self.field.validate, 'c')
        self.assertRaises(errors.ValidationError, self.field.validate, 'd')
        self.assertRaises(errors.ValidationError, self.field.validate, 1)
        self.assertRaises(errors.ValidationError, self.field.validate, 2)


class TestIntParam(TestCase):

    def setUp(self):
        self.field = params.IntParam()

    def test_inheritance(self):
        self.assertTrue(isinstance(self.field, params.ResourceParam))

    def test_validator_type(self):
        self.assertEqual(self.field.validator_type, validators.IntValidator)

    def test_param_usage(self):
        self.assertEqual(self.field.validate(10), 10)

    def test_param_invalid_values(self):
        self.assertRaises(errors.ValidationError, self.field.validate, 'abc')
        self.assertRaises(errors.ValidationError, self.field.validate,
                          datetime.datetime.utcnow())

    def test_param_options(self):
        self.field.flags['options'] = {'a', 'b', 1, 2}
        self.assertEqual(self.field.validate(1), 1)
        self.assertEqual(self.field.validate(2), 2)
        self.assertEqual(self.field.validate(None), None)
        self.assertEqual(self.field.validate(NotSet), NotSet)
        self.assertRaises(errors.ValidationError, self.field.validate, 'c')
        self.assertRaises(errors.ValidationError, self.field.validate, 'd')
        self.assertRaises(errors.ValidationError, self.field.validate, 3)
        self.assertRaises(errors.ValidationError, self.field.validate, 4)
        self.field.flags['options'] = ['a', 'b', 1, 2]
        self.assertEqual(self.field.validate(1), 1)
        self.assertEqual(self.field.validate(2), 2)
        self.assertEqual(self.field.validate(None), None)
        self.assertEqual(self.field.validate(NotSet), NotSet)
        self.assertRaises(errors.ValidationError, self.field.validate, 'c')
        self.assertRaises(errors.ValidationError, self.field.validate, 'd')
        self.assertRaises(errors.ValidationError, self.field.validate, 3)
        self.assertRaises(errors.ValidationError, self.field.validate, 4)


class TestBoolParam(TestCase):

    def setUp(self):
        self.field = params.BoolParam()

    def test_inheritance(self):
        self.assertTrue(isinstance(self.field, params.ResourceParam))

    def test_validator_type(self):
        self.assertEqual(self.field.validator_type, validators.BoolValidator)

    def test_param_usage(self):
        self.assertEqual(self.field.validate(True), True)

    def test_param_invalid_values(self):
        self.assertRaises(errors.ValidationError, self.field.validate, 'abc')
        self.assertRaises(errors.ValidationError, self.field.validate,
                          datetime.datetime.utcnow())
        self.assertRaises(errors.ValidationError, self.field.validate, 10)

    def test_param_options(self):
        self.field.flags['options'] = {'a', 'b', False}
        self.assertEqual(self.field.validate(False), False)
        self.assertEqual(self.field.validate(None), None)
        self.assertEqual(self.field.validate(NotSet), NotSet)
        self.assertRaises(errors.ValidationError, self.field.validate, 'c')
        self.assertRaises(errors.ValidationError, self.field.validate, 'd')
        self.assertRaises(errors.ValidationError, self.field.validate, True)
        self.assertRaises(errors.ValidationError, self.field.validate, 1)
        self.field.flags['options'] = ['a', 'b', 1, False]
        # True in {1} returns True
        self.assertEqual(self.field.validate(True), True)
        self.assertEqual(self.field.validate(False), False)
        self.assertEqual(self.field.validate(None), None)
        self.assertEqual(self.field.validate(NotSet), NotSet)
        self.assertRaises(errors.ValidationError, self.field.validate, 'c')
        self.assertRaises(errors.ValidationError, self.field.validate, 'd')


class TestDecimalParam(TestCase):

    def setUp(self):
        self.field = params.DecimalParam()

    def test_inheritance(self):
        self.assertTrue(isinstance(self.field, params.ResourceParam))

    def test_validator_type(self):
        self.assertEqual(self.field.validator_type,
                         validators.DecimalValidator)

    def test_param_usage(self):
        self.assertEqual(self.field.validate(5.234), 5.234)

    def test_param_invalid_values(self):
        self.assertRaises(errors.ValidationError, self.field.validate, 'abc')
        self.assertRaises(errors.ValidationError, self.field.validate,
                          datetime.datetime.utcnow())

    def test_param_options(self):
        self.field.flags['options'] = {'a', 'b', 1.3, 2.4}
        self.assertEqual(self.field.validate(1.3), 1.3)
        self.assertEqual(self.field.validate(2.4), 2.4)
        self.assertEqual(self.field.validate(None), None)
        self.assertEqual(self.field.validate(NotSet), NotSet)
        self.assertRaises(errors.ValidationError, self.field.validate, 'c')
        self.assertRaises(errors.ValidationError, self.field.validate, 'd')
        self.assertRaises(errors.ValidationError, self.field.validate, 3)
        self.assertRaises(errors.ValidationError, self.field.validate, 4)
        self.assertRaises(errors.ValidationError, self.field.validate, 2.44)
        self.assertRaises(errors.ValidationError, self.field.validate, 2)
        self.field.flags['options'] = ['a', 'b', 1.3, 2.4]
        self.assertEqual(self.field.validate(1.3), 1.3)
        self.assertEqual(self.field.validate(2.4), 2.4)
        self.assertEqual(self.field.validate(None), None)
        self.assertEqual(self.field.validate(NotSet), NotSet)
        self.assertRaises(errors.ValidationError, self.field.validate, 'a')
        self.assertRaises(errors.ValidationError, self.field.validate, 'b')
        self.assertRaises(errors.ValidationError, self.field.validate, 3)
        self.assertRaises(errors.ValidationError, self.field.validate, 4)
        self.assertRaises(errors.ValidationError, self.field.validate, 2.44)
        self.assertRaises(errors.ValidationError, self.field.validate, 2)


class TestDateParam(TestCase):

    def setUp(self):
        self.field = params.DateParam()

    def test_inheritance(self):
        self.assertTrue(isinstance(self.field, params.ResourceParam))

    def test_validator_type(self):
        self.assertEqual(self.field.validator_type, validators.DateValidator)

    def test_param_usage(self):
        dt = datetime.date.today()
        self.assertEqual(self.field.validate(dt), dt)

    def test_param_invalid_values(self):
        self.assertRaises(errors.ValidationError, self.field.validate, 'abc')
        self.assertRaises(errors.ValidationError, self.field.validate, 10,
                          False)
        self.assertRaises(errors.ValidationError, self.field.validate, True)

    def test_param_options(self):
        dt = datetime.date(2011, 10, 12)
        self.field.flags['options'] = {'a', 3435, dt}
        self.assertEqual(self.field.validate(dt), dt)
        self.assertEqual(self.field.validate(None), None)
        self.assertEqual(self.field.validate(NotSet), NotSet)
        self.assertRaises(errors.ValidationError, self.field.validate,
                          datetime.date.today())
        self.assertRaises(errors.ValidationError, self.field.validate, 'a')
        self.assertRaises(errors.ValidationError, self.field.validate, 3435)


class TestDateTimeParam(TestCase):

    def setUp(self):
        self.field = params.DateTimeParam()

    def test_inheritance(self):
        self.assertTrue(isinstance(self.field, params.ResourceParam))

    def test_validator_type(self):
        self.assertEqual(self.field.validator_type,
                         validators.DateTimeValidator)

    def test_param_usage(self):
        dt = datetime.datetime.utcnow()
        self.assertEqual(self.field.validate(dt), dt)

    def test_param_invalid_values(self):
        self.assertRaises(errors.ValidationError, self.field.validate, 'abc')
        self.assertRaises(errors.ValidationError, self.field.validate, 10,
                          False)
        self.assertRaises(errors.ValidationError, self.field.validate, True)

    def test_param_options(self):
        dt = datetime.datetime(2011, 10, 12)
        self.field.flags['options'] = {'a', 3435, dt}
        self.assertEqual(self.field.validate(dt), dt)
        self.assertEqual(self.field.validate(None), None)
        self.assertEqual(self.field.validate(NotSet), NotSet)
        self.assertRaises(errors.ValidationError, self.field.validate,
                          datetime.datetime.utcnow())
        self.assertRaises(errors.ValidationError, self.field.validate, 'a')
        self.assertRaises(errors.ValidationError, self.field.validate, 3435)


class TestListParam(TestCase):

    def setUp(self):
        self.param = params.ListParam()

    def test_inheritance(self):
        self.assertTrue(isinstance(self.param, params.ResourceParam))

    def test_validator_type(self):
        self.assertEqual(self.param.validator_type, validators.ListValidator)

    def test_param_usage(self):
        self.assertEqual(self.param.validate([]), [])
        self.assertEqual(self.param.validate([1, 2, 3]), [1, 2, 3])
        self.assertEqual(self.param.validate(['1', '2', '3']),
                         ['1', '2', '3'])

    def test_param_invalid_values(self):
        self.assertRaises(errors.ValidationError, self.param.validate, 4)

    def test_param_list_item_type_int(self):
        self.assertRaises(errors.ValidationError, params.ListParam,
                          item_type=fields.IntField())
        param = params.ListParam(item_type=params.IntParam())
        self.assertEqual(param.validate(()), [])
        self.assertEqual(param.validate('1,2,3'), [1, 2, 3])
        self.assertEqual(param.validate((1, 2, 3)), [1, 2, 3])
        self.assertEqual(param.validate(('1', '2', '3')), [1, 2, 3])
        self.assertRaises(errors.ValidationError, param.validate, 'abc')
        self.assertRaises(errors.ValidationError, param.validate,
                          ['abc', 'efd'])
        self.assertRaises(errors.ValidationError, param.validate, False)
        self.assertRaises(errors.ValidationError, param.validate,
                          ['abc', 'ef'])

    def test_param_list_item_type_char(self):
        self.assertRaises(errors.ValidationError, params.ListParam,
                          item_type=fields.CharField())
        param = params.ListParam(item_type=params.CharParam())
        self.assertEqual(param.validate([]), [])
        self.assertEqual(param.validate(()), [])
        self.assertEqual(param.validate('abd'), ['abd'])
        self.assertEqual(param.validate('1,2,3'), ['1', '2', '3'])
        self.assertEqual(param.validate(('1', '2', '3')), ['1', '2', '3'])
        self.assertEqual(param.validate((1, 2, 3)), ['1', '2', '3'])
        self.assertRaises(errors.ValidationError, param.validate, 1)
        self.assertRaises(errors.ValidationError, param.validate, False)

    def test_param_list_item_type_bool(self):
        self.assertRaises(errors.ValidationError, params.ListParam,
                          item_type=fields.BoolField())
        param = params.ListParam(item_type=params.BoolParam())
        self.assertEqual(param.validate([]), [])
        self.assertEqual(param.validate([True, False, 1, 0]),
                         [True, False, True, False])
        self.assertEqual(param.validate(['0', '1']), [False, True])
        self.assertEqual(param.validate([0, 1]), [False, True])
        self.assertEqual(param.validate(()), [])
        self.assertEqual(param.validate((True, False, 1, 0)),
                         [True, False, True, False])
        self.assertEqual(param.validate(('0', '1')), [False, True])
        self.assertEqual(param.validate((0, 1)), [False, True])
        self.assertRaises(errors.ValidationError, param.validate,
                          ['abc', 'edf'])
        self.assertRaises(errors.ValidationError, param.validate, [2])
        self.assertRaises(errors.ValidationError, param.validate, 4)
        self.assertRaises(errors.ValidationError, param.validate, (1, 2, 3))

    def test_param_list_item_type_decimal(self):
        self.assertRaises(errors.ValidationError, params.ListParam,
                          item_type=fields.DecimalField())
        param = params.ListParam(item_type=params.DecimalParam())
        self.assertEqual(param.validate([]), [])
        self.assertEqual(param.validate([0, 1, 1.123, -123]),
                         [0, 1, 1.123, -123])
        self.assertEqual(param.validate(['0.123', '1']), [0.123, 1])
        self.assertEqual(param.validate([True, False]), [1, 0])
        self.assertEqual(param.validate(()), [])
        self.assertEqual(param.validate((0, 1, 1.123, -123)),
                         [0, 1, 1.123, -123])
        self.assertEqual(param.validate(('0.123', '1')), [0.123, 1])
        self.assertRaises(errors.ValidationError, param.validate,
                          ['abc', 'edf'])
        self.assertRaises(errors.ValidationError, param.validate, False)
        self.assertRaises(errors.ValidationError, param.validate,
                          ('asdf', 2, 3))

    def test_param_list_item_type_list(self):
        self.assertRaises(errors.ValidationError, params.ListParam,
                          item_type=fields.ListField())
        param = params.ListParam(
            item_type=params.ListParam(item_type=params.IntParam())
        )
        self.assertEqual(param.validate([]), [])
        self.assertEqual(param.validate([[1, 2, 3], [True, False], [1.2]]),
                         [[1, 2, 3], [1, 0], [1]])
        self.assertRaises(errors.ValidationError, param.validate,
                          [[1, 2, 3], 4, [1.2]])

    def test_param_options(self):
        self.param.flags['options'] = ['a', 'b', 1, 2, 3]
        self.assertEqual(self.param.validate([]), [])
        self.assertEqual(self.param.validate([1, 2]), [1, 2])
        self.assertEqual(self.param.validate(['a']), ['a'])
        self.assertEqual(self.param.validate(['a', 'b']), ['a', 'b'])
        self.assertEqual(self.param.validate(None), None)
        self.assertEqual(self.param.validate(NotSet), NotSet)
        self.assertRaises(errors.ValidationError, self.param.validate, 'c')
        self.assertRaises(errors.ValidationError, self.param.validate, 4)
        self.assertRaises(
            errors.ValidationError, self.param.validate, ['a', 'b', 'c']
        )
