from unittest import TestCase, mock
from thorium import fields, errors
import datetime
import types


class TestNotSet(TestCase):

    def setUp(self):
        self.field = fields.NotSet

    def test_notset_is_equal_to_notset(self):
        self.assertEqual(self.field, fields.NotSet)
        self.assertEqual(fields.NotSet, fields.NotSet)

    def test_notset_is_not_none(self):
        self.assertNotEqual(fields.NotSet, None)

    def test_notset_is_not_false(self):
        self.assertNotEqual(fields.NotSet, False)

    def test_notset_is_not_true(self):
        self.assertNotEqual(fields.NotSet, True)

    def test_notset_is_falsey(self):
        self.assertEqual(bool(fields.NotSet), False)
        if self.field:
            self.fail('Notset should be falsey')
        hit = False
        if not self.field:
            hit = True
        self.assertTrue(hit)


class TestFieldValidator(TestCase):

    def setUp(self):
        field = mock.MagicMock()
        field.flags = {}
        field.flags['notnull'] = True
        self.validator = fields.FieldValidator(field)

    def test_validate(self):
        self.assertRaises(NotImplementedError, self.validator.validate, 10)

    def test_validate_notnull(self):
        self.assertRaises(errors.ValidationError, self.validator.validate, None)

    def test_validate_notset(self):
        self.assertEqual(self.validator.validate(fields.NotSet), fields.NotSet)

    def test_validate_with_nullable_field(self):
        field = mock.MagicMock()
        field.flags = {}
        field.flags['notnull'] = False
        validator_nullable = fields.FieldValidator(field)
        self.assertEqual(validator_nullable.validate(None), None)

    def test_validate(self):
        self.assertRaises(NotImplementedError, self.validator.validate, 10)

    def test_validate_returns_value(self):
        def func(self, value):
            return value

        self.validator.validate = types.MethodType(func, self.validator)
        self.assertEqual(self.validator.validate(True), True)
        self.assertEqual(self.validator.validate(False), False)
        self.assertEqual(self.validator.validate(10), 10)


class TestCharValidator(TestCase):

    def setUp(self):
        char_field = mock.MagicMock(fields.CharField)
        char_field.flags = {}
        char_field.flags['max_length'] = 10
        char_field.flags['notnull'] = True
        self.validator = fields.CharValidator(char_field)

    def test_validate(self):
        result = self.validator.validate('test1')
        self.assertEqual('test1', result)

    def test_int_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.validate, 1)

    def test_bool_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.validate, True)

    def test_date_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.validate, datetime.datetime)

    def test_max_length(self):
        self.assertRaises(errors.ValidationError, self.validator.validate, 'longer than 10 characters')


class TestIntValidator(TestCase):

    def setUp(self):
        self.validator = fields.IntValidator(mock.MagicMock())

    def test_validate(self):
        result = self.validator.validate(42)
        self.assertEqual(42, result)

    def test_long_validation(self):
        result = self.validator.validate(420000000000000000000000000)
        self.assertEqual(420000000000000000000000000, result)

    def test_str_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.validate, 'abc')

    def test_bool_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.validate, True)

    def test_date_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.validate, datetime.datetime)


class TestDateTimeValidator(TestCase):

    def setUp(self):
        self.validator = fields.DateTimeValidator(mock.MagicMock())

    def test_validate(self):
        dt = datetime.datetime.utcnow()
        result = self.validator.validate(dt)
        self.assertEqual(dt, result)

    def test_str_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.validate, 'abc')

    def test_bool_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.validate, True)

    def test_int_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.validate, 1)


class TestDecimalValidator(TestCase):

    def setUp(self):
        self.validator = fields.DecimalValidator(mock.MagicMock())

    def test_validate(self):
        result = self.validator.validate(4.2)
        self.assertEqual(4.2, result)

    def test_str_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.validate, 'abc')

    def test_bool_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.validate, True)

    def test_date_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.validate, datetime.datetime)


class TestBoolValidator(TestCase):

    def setUp(self):
        self.validator = fields.BoolValidator(mock.MagicMock())

    def test_validate(self):
        result = self.validator.validate(True)
        self.assertEqual(result, True)
        result = self.validator.validate(False)
        self.assertEqual(result, False)

    def test_str_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.validate, 'abc')

    def test_int_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.validate, 92)

    def test_date_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.validate, datetime.datetime)

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
        self.assertRaises(errors.ValidationError, self.validator.validate, 2, True)
        self.assertRaises(errors.ValidationError, self.validator.validate, 'tRuE', True)
        self.assertRaises(errors.ValidationError, self.validator.validate, -1, True)


class TestListValidator(TestCase):

    def setUp(self):
        list_field = mock.MagicMock(fields.ListField)
        list_field.flags = {}
        list_field.flags['item_type'] = fields.IntField()
        list_field.flags['notnull'] = True
        self.validator = fields.ListValidator(list_field)

    def test_validate(self):
        self.assertEqual(self.validator.validate([]), [])
        self.assertTrue(self.validator.validate([5, 3, 1]))
        self.assertTrue(self.validator.validate(['1', '2', '3']))

    def test_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.validate, 'abc')
        self.assertRaises(errors.ValidationError, self.validator.validate, ['1', 'abc'])
        self.assertRaises(errors.ValidationError, self.validator.validate, '1,2,3,4')

    def test_cast(self):
        self.assertTrue(self.validator.validate((1, 2, 3), cast=True))
        self.assertRaises(errors.ValidationError, self.validator.validate, (1, 2, 3), False)


class SimpleValidator(fields.FieldValidator):

    def validate(self, value, cast=False):
        return value


class SimpleTypedField(fields.TypedField):
        validator_type = SimpleValidator


class TestTypedField(TestCase):

    def setUp(self):
        self.field = SimpleTypedField()

    def test_init(self):
        self.assertRaises(NotImplementedError, fields.TypedField)

        simple = SimpleTypedField()
        self.assertEqual(simple.name, 'noname')
        self.assertEqual(simple.flags['notnull'], False)
        self.assertEqual(simple.flags['default'], fields.NotSet)
        self.assertEqual(simple.flags['readonly'], False)
        self.assertEqual(simple._value, fields.NotSet)

        with_default = SimpleTypedField(default=10)
        self.assertEqual(with_default.flags['notnull'], False)
        self.assertEqual(with_default.flags['default'], 10)
        self.assertEqual(with_default.flags['readonly'], False)
        self.assertEqual(with_default._value, 10)

        with_notnull = SimpleTypedField(notnull=True)
        self.assertEqual(with_notnull.flags['notnull'], True)
        self.assertEqual(with_notnull.flags['default'], fields.NotSet)
        self.assertEqual(with_default.flags['readonly'], False)
        self.assertEqual(with_notnull._value, fields.NotSet)

        with_default = SimpleTypedField(readonly=True)
        self.assertEqual(with_default.flags['notnull'], False)
        self.assertEqual(with_default.flags['default'], fields.NotSet)
        self.assertEqual(with_default.flags['readonly'], True)
        self.assertEqual(with_default._value, fields.NotSet)

    def test_set_with_notset(self):
        self.assertEqual(self.field.set(fields.NotSet), fields.NotSet)
        self.assertEqual(self.field._value, fields.NotSet)

    def test_set_with_value(self):
        self.assertEqual(self.field.set(10), 10)
        self.assertEqual(self.field._value, 10)

    def test_set_calls_validator(self):
        self.field._validator = mock.MagicMock()
        self.field.set(10)
        self.field._validator.validate.assert_called_once_with(10, False)

    def test_get_with_value(self):
        self.field._value = 10
        self.assertEqual(self.field.get(), 10)

    def test_get_notset_with_default(self):
        self.assertEqual(self.field._value, fields.NotSet)
        self.field.default = 'abc'
        self.assertEqual(self.field.get(), fields.NotSet)

    def test_get_notset_without_default(self):
        self.assertEqual(self.field._value, fields.NotSet)
        self.assertEqual(self.field.flags['default'], fields.NotSet)
        self.assertEqual(self.field.get(), fields.NotSet)

    def test_to_default(self):
        self.field._value = 'abc'
        self.assertEqual(self.field.flags['default'], fields.NotSet)
        self.assertEqual(self.field.to_default(), fields.NotSet)
        self.assertEqual(self.field._value, fields.NotSet)

        self.field.flags['default'] = 10
        self.assertEqual(self.field.to_default(), 10)
        self.assertEqual(self.field._value, 10)

    def test_is_set(self):
        self.assertEqual(self.field._value, fields.NotSet)
        self.assertEqual(self.field.is_set(), False)

        self.field._value = 10
        self.assertEqual(self.field.is_set(), True)

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
        self.assertEqual(self.field.validator_type, fields.CharValidator)

    def test_set_unique_attributes(self):
        self.assertEqual(self.field.flags['max_length'], None)
        self.field.set_unique_attributes(max_length=99)
        self.assertEqual(self.field.flags['max_length'], 99)

    def test_field_usage(self):
        self.assertEqual(self.field.set('hello world!'), self.field.get())

    def test_field_maxlength(self):
        self.field.flags['max_length'] = 5
        self.assertRaises(errors.ValidationError, self.field.set, 'too long for max_length')

    def test_field_invalid_values(self):
        self.assertRaises(errors.ValidationError, self.field.set, 10)
        self.assertRaises(errors.ValidationError, self.field.set, datetime.datetime.utcnow())
        self.assertRaises(errors.ValidationError, self.field.set, True)


class TestIntField(TestCase):

    def setUp(self):
        self.field = fields.IntField()

    def test_inheritance(self):
        self.assertTrue(isinstance(self.field, fields.ResourceField))

    def test_validator_type(self):
        self.assertEqual(self.field.validator_type, fields.IntValidator)

    def test_field_usage(self):
        self.assertEqual(self.field.set(10), self.field.get())

    def test_field_invalid_values(self):
        self.assertRaises(errors.ValidationError, self.field.set, 'abc')
        self.assertRaises(errors.ValidationError, self.field.set, datetime.datetime.utcnow())
        self.assertRaises(errors.ValidationError, self.field.set, True)


class TestBoolField(TestCase):

    def setUp(self):
        self.field = fields.BoolField()

    def test_inheritance(self):
        self.assertTrue(isinstance(self.field, fields.ResourceField))

    def test_validator_type(self):
        self.assertEqual(self.field.validator_type, fields.BoolValidator)

    def test_field_usage(self):
        self.assertEqual(self.field.set(True), self.field.get())

    def test_field_invalid_values(self):
        self.assertRaises(errors.ValidationError, self.field.set, 'abc')
        self.assertRaises(errors.ValidationError, self.field.set, datetime.datetime.utcnow())
        self.assertRaises(errors.ValidationError, self.field.set, 10)


class TestDecimalField(TestCase):

    def setUp(self):
        self.field = fields.DecimalField()

    def test_inheritance(self):
        self.assertTrue(isinstance(self.field, fields.ResourceField))

    def test_validator_type(self):
        self.assertEqual(self.field.validator_type, fields.DecimalValidator)

    def test_field_usage(self):
        self.assertEqual(self.field.set(5.234), self.field.get())

    def test_field_invalid_values(self):
        self.assertRaises(errors.ValidationError, self.field.set, 'abc')
        self.assertRaises(errors.ValidationError, self.field.set, datetime.datetime.utcnow())
        self.assertRaises(errors.ValidationError, self.field.set, True)


class TestDateTimeField(TestCase):

    def setUp(self):
        self.field = fields.DateTimeField()

    def test_inheritance(self):
        self.assertTrue(isinstance(self.field, fields.ResourceField))

    def test_validator_type(self):
        self.assertEqual(self.field.validator_type, fields.DateTimeValidator)

    def test_field_usage(self):
        self.assertEqual(self.field.set(datetime.datetime.utcnow()), self.field.get())

    def test_field_invalid_values(self):
        self.assertRaises(errors.ValidationError, self.field.set, 'abc')
        self.assertRaises(errors.ValidationError, self.field.set, 10, False)
        self.assertRaises(errors.ValidationError, self.field.set, True)


class TestListField(TestCase):

    def setUp(self):
        self.field = fields.ListField()

    def test_inheritance(self):
        self.assertTrue(isinstance(self.field, fields.ResourceField))

    def test_validator_type(self):
        self.assertEqual(self.field.validator_type, fields.ListValidator)

    def test_field_usage(self):
        self.assertEqual(self.field.set([]), self.field.get())
        self.assertEqual(self.field.set([1, 2, 3]), self.field.get())
        self.assertEqual(self.field.set(['1', '2', '3']), ['1', '2', '3'])
        self.assertEqual(self.field.set((), cast=True), [])
        self.assertEqual(self.field.set((1, 2, 3), cast=True), [1, 2, 3])
        self.assertEqual(self.field.set(('1', '2', '3'), cast=True), ['1', '2', '3'])

    def test_field_invalid_values(self):
        self.assertRaises(errors.ValidationError, self.field.set, 4)
        self.assertRaises(errors.ValidationError, self.field.set, ())
        self.assertRaises(errors.ValidationError, self.field.set, (1, 2, 3))

    def test_field_list_item_type_int(self):
        self.assertRaises(errors.ValidationError, fields.ListField, item_type=fields.IntParam())
        field = fields.ListField(item_type=fields.IntField())
        self.assertEqual(field.set([]), field.get())
        self.assertEqual(field.set([1, 2, 3]), field.get())
        self.assertEqual(field.set(['1', '2', '3']), [1, 2, 3])
        self.assertEqual(field.set((), cast=True), [])
        self.assertEqual(field.set((1, 2, 3), cast=True), [1, 2, 3])
        self.assertEqual(field.set(('1', '2', '3'), cast=True), [1, 2, 3])
        self.assertRaises(errors.ValidationError, field.set, 'abc')
        self.assertRaises(errors.ValidationError, field.set, ['abc', 'efd'])
        self.assertRaises(errors.ValidationError, field.set, ())
        self.assertRaises(errors.ValidationError, field.set, (1, 2, 3))

    def test_field_list_item_type_char(self):
        self.assertRaises(errors.ValidationError, fields.ListField, item_type=fields.CharParam())
        field = fields.ListField(item_type=fields.CharField())
        self.assertEqual(field.set([]), field.get())
        self.assertEqual(field.set(['1', '2', '3']), field.get())
        self.assertEqual(field.set([1, 2, 3]), ['1', '2', '3'])
        self.assertEqual(field.set((), cast=True), [])
        self.assertEqual(field.set(('1', '2', '3'), cast=True), ['1', '2', '3'])
        self.assertEqual(field.set((1, 2, 3), cast=True), ['1', '2', '3'])
        self.assertRaises(errors.ValidationError, field.set, ())
        self.assertRaises(errors.ValidationError, field.set, (1, 2, 3))

    def test_field_list_item_type_bool(self):
        self.assertRaises(errors.ValidationError, fields.ListField, item_type=fields.BoolParam())
        field = fields.ListField(item_type=fields.BoolField())
        self.assertEqual(field.set([]), field.get())
        self.assertEqual(field.set([True, False, 1, 0]), [True, False, True, False])
        self.assertEqual(field.set(['0', '1']), [False, True])
        self.assertEqual(field.set([0, 1]), [False, True])
        self.assertEqual(field.set((), cast=True), [])
        self.assertEqual(field.set((True, False, 1, 0), cast=True), [True, False, True, False])
        self.assertEqual(field.set(('0', '1'), cast=True), [False, True])
        self.assertEqual(field.set((0, 1), cast=True), [False, True])
        self.assertRaises(errors.ValidationError, field.set, ['abc', 'edf'])
        self.assertRaises(errors.ValidationError, field.set, [2])
        self.assertRaises(errors.ValidationError, field.set, ())
        self.assertRaises(errors.ValidationError, field.set, (1, 2, 3))

    def test_field_list_item_type_decimal(self):
        self.assertRaises(errors.ValidationError, fields.ListField, item_type=fields.DecimalParam())
        field = fields.ListField(item_type=fields.DecimalField())
        self.assertEqual(field.set([]), field.get())
        self.assertEqual(field.set([0, 1, 1.123, -123]), field.get())
        self.assertEqual(field.set(['0.123', '1']), [0.123, 1])
        self.assertEqual(field.set([True, False]), [1, 0])
        self.assertEqual(field.set((), cast=True), [])
        self.assertEqual(field.set((0, 1, 1.123, -123), cast=True), field.get())
        self.assertEqual(field.set(('0.123', '1'), cast=True), [0.123, 1])
        self.assertRaises(errors.ValidationError, field.set, ['abc', 'edf'])
        self.assertRaises(errors.ValidationError, field.set, ())
        self.assertRaises(errors.ValidationError, field.set, (1, 2, 3))

    def test_field_list_item_type_datetime(self):
        pass

    def test_field_list_item_type_list(self):
        self.assertRaises(errors.ValidationError, fields.ListField, item_type=fields.ListParam())
        field = fields.ListField(item_type=fields.ListField(item_type=fields.IntField()))
        self.assertEqual(field.set([]), field.get())
        self.assertEqual(field.set([[1, 2, 3], [True, False], [1.2]]), [[1, 2, 3], [1, 0], [1]])
        self.assertRaises(errors.ValidationError, field.set, [[1, 2, 3], 4, [1.2]])

    def test_field_list_item_type_dict(self):
        pass


class TestCharParam(TestCase):

    def setUp(self):
        self.field = fields.CharParam()

    def test_inheritance(self):
        self.assertTrue(isinstance(self.field, fields.ResourceParam))

    def test_validator_type(self):
        self.assertEqual(self.field.validator_type, fields.CharValidator)

    def test_set_unique_attributes(self):
        self.assertEqual(self.field.flags['max_length'], None)
        self.field.set_unique_attributes(max_length=99)
        self.assertEqual(self.field.flags['max_length'], 99)

    def test_param_usage(self):
        self.assertEqual(self.field.set('hello world!'), self.field.get())

    def test_param_maxlength(self):
        self.field.flags['max_length'] = 5
        self.assertRaises(errors.ValidationError, self.field.set, 'too long for max_length')

    def test_param_invalid_values(self):
        self.assertRaises(errors.ValidationError, self.field.set, 10)
        self.assertRaises(errors.ValidationError, self.field.set, datetime.datetime.utcnow())
        self.assertRaises(errors.ValidationError, self.field.set, True)


class TestIntParam(TestCase):

    def setUp(self):
        self.field = fields.IntParam()

    def test_inheritance(self):
        self.assertTrue(isinstance(self.field, fields.ResourceParam))

    def test_validator_type(self):
        self.assertEqual(self.field.validator_type, fields.IntValidator)

    def test_param_usage(self):
        self.assertEqual(self.field.set(10), self.field.get())

    def test_param_invalid_values(self):
        self.assertRaises(errors.ValidationError, self.field.set, 'abc')
        self.assertRaises(errors.ValidationError, self.field.set, datetime.datetime.utcnow())


class TestBoolParam(TestCase):

    def setUp(self):
        self.field = fields.BoolParam()

    def test_inheritance(self):
        self.assertTrue(isinstance(self.field, fields.ResourceParam))

    def test_validator_type(self):
        self.assertEqual(self.field.validator_type, fields.BoolValidator)

    def test_param_usage(self):
        self.assertEqual(self.field.set(True), self.field.get())

    def test_param_invalid_values(self):
        self.assertRaises(errors.ValidationError, self.field.set, 'abc')
        self.assertRaises(errors.ValidationError, self.field.set, datetime.datetime.utcnow())
        self.assertRaises(errors.ValidationError, self.field.set, 10)


class TestDecimalParam(TestCase):

    def setUp(self):
        self.field = fields.DecimalParam()

    def test_inheritance(self):
        self.assertTrue(isinstance(self.field, fields.ResourceParam))

    def test_validator_type(self):
        self.assertEqual(self.field.validator_type, fields.DecimalValidator)

    def test_param_usage(self):
        self.assertEqual(self.field.set(5.234), self.field.get())

    def test_param_invalid_values(self):
        self.assertRaises(errors.ValidationError, self.field.set, 'abc')
        self.assertRaises(errors.ValidationError, self.field.set, datetime.datetime.utcnow())


class TestDateTimeParam(TestCase):

    def setUp(self):
        self.field = fields.DateTimeParam()

    def test_inheritance(self):
        self.assertTrue(isinstance(self.field, fields.ResourceParam))

    def test_validator_type(self):
        self.assertEqual(self.field.validator_type, fields.DateTimeValidator)

    def test_param_usage(self):
        self.assertEqual(self.field.set(datetime.datetime.utcnow()), self.field.get())

    def test_param_invalid_values(self):
        self.assertRaises(errors.ValidationError, self.field.set, 'abc')
        self.assertRaises(errors.ValidationError, self.field.set, 10, False)
        self.assertRaises(errors.ValidationError, self.field.set, True)
        
        
class TestListParam(TestCase):

    def setUp(self):
        self.param = fields.ListParam()

    def test_inheritance(self):
        self.assertTrue(isinstance(self.param, fields.ResourceParam))

    def test_validator_type(self):
        self.assertEqual(self.param.validator_type, fields.ListValidator)

    def test_param_usage(self):
        self.assertEqual(self.param.set([]), self.param.get())
        self.assertEqual(self.param.set([1, 2, 3]), self.param.get())
        self.assertEqual(self.param.set(['1', '2', '3']), ['1', '2', '3'])
        self.assertEqual(self.param.set((), cast=True), [])
        self.assertEqual(self.param.set((1, 2, 3), cast=True), [1, 2, 3])
        self.assertEqual(self.param.set(('1', '2', '3'), cast=True), ['1', '2', '3'])

    def test_param_invalid_values(self):
        self.assertRaises(errors.ValidationError, self.param.set, 4)
        self.assertRaises(errors.ValidationError, self.param.set, ())
        self.assertRaises(errors.ValidationError, self.param.set, (1, 2, 3))

    def test_param_list_item_type_int(self):
        self.assertRaises(errors.ValidationError, fields.ListParam, item_type=fields.IntField())
        param = fields.ListParam(item_type=fields.IntParam())
        self.assertEqual(param.set([]), param.get())
        self.assertEqual(param.set([1, 2, 3, -1]), param.get())
        self.assertEqual(param.set([1, 2.23]), [1, 2])
        self.assertEqual(param.set(['1', '2', '3']), [1, 2, 3])
        self.assertEqual(param.set((), cast=True), [])
        self.assertEqual(param.set((1, 2, 3), cast=True), [1, 2, 3])
        self.assertEqual(param.set(('1', '2', '3'), cast=True), [1, 2, 3])
        self.assertRaises(errors.ValidationError, param.set, 'abc')
        self.assertRaises(errors.ValidationError, param.set, ['abc', 'efd'])
        self.assertRaises(errors.ValidationError, param.set, ())
        self.assertRaises(errors.ValidationError, param.set, (1, 2, 3))

    def test_param_list_item_type_char(self):
        self.assertRaises(errors.ValidationError, fields.ListParam, item_type=fields.CharField())
        param = fields.ListParam(item_type=fields.CharParam())
        self.assertEqual(param.set([]), param.get())
        self.assertEqual(param.set(['1', '2', '3']), param.get())
        self.assertEqual(param.set([1, 2, 3]), ['1', '2', '3'])
        self.assertEqual(param.set((), cast=True), [])
        self.assertEqual(param.set(('1', '2', '3'), cast=True), ['1', '2', '3'])
        self.assertEqual(param.set((1, 2, 3), cast=True), ['1', '2', '3'])
        self.assertRaises(errors.ValidationError, param.set, ())
        self.assertRaises(errors.ValidationError, param.set, (1, 2, 3))

    def test_param_list_item_type_bool(self):
        self.assertRaises(errors.ValidationError, fields.ListParam, item_type=fields.BoolField())
        param = fields.ListParam(item_type=fields.BoolParam())
        self.assertEqual(param.set([]), param.get())
        self.assertEqual(param.set([True, False, 1, 0]), [True, False, True, False])
        self.assertEqual(param.set(['0', '1']), [False, True])
        self.assertEqual(param.set([0, 1]), [False, True])
        self.assertEqual(param.set((), cast=True), [])
        self.assertEqual(param.set((True, False, 1, 0), cast=True), [True, False, True, False])
        self.assertEqual(param.set(('0', '1'), cast=True), [False, True])
        self.assertEqual(param.set((0, 1), cast=True), [False, True])
        self.assertRaises(errors.ValidationError, param.set, ['abc', 'edf'])
        self.assertRaises(errors.ValidationError, param.set, [2])
        self.assertRaises(errors.ValidationError, param.set, ())
        self.assertRaises(errors.ValidationError, param.set, (1, 2, 3))

    def test_param_list_item_type_decimal(self):
        self.assertRaises(errors.ValidationError, fields.ListParam, item_type=fields.DecimalField())
        param = fields.ListParam(item_type=fields.DecimalParam())
        self.assertEqual(param.set([]), param.get())
        self.assertEqual(param.set([0, 1, 1.123, -123]), param.get())
        self.assertEqual(param.set(['0.123', '1']), [0.123, 1])
        self.assertEqual(param.set([True, False]), [1, 0])
        self.assertEqual(param.set((), cast=True), [])
        self.assertEqual(param.set((0, 1, 1.123, -123), cast=True), param.get())
        self.assertEqual(param.set(('0.123', '1'), cast=True), [0.123, 1])
        self.assertRaises(errors.ValidationError, param.set, ['abc', 'edf'])
        self.assertRaises(errors.ValidationError, param.set, ())
        self.assertRaises(errors.ValidationError, param.set, (1, 2, 3))

    def test_param_list_item_type_datetime(self):
        pass

    def test_param_list_item_type_list(self):
        self.assertRaises(errors.ValidationError, fields.ListParam, item_type=fields.ListField())
        param = fields.ListParam(item_type=fields.ListParam(item_type=fields.IntParam()))
        self.assertEqual(param.set([]), param.get())
        self.assertEqual(param.set([[1, 2, 3], [True, False], [1.2]]), [[1, 2, 3], [1, 0], [1]])
        self.assertRaises(errors.ValidationError, param.set, [[1, 2, 3], 4, [1.2]])

    def test_param_list_item_type_dict(self):
        pass