from unittest import TestCase, mock
from thorium import fields, errors
import datetime
import types


class TestFieldValidator(TestCase):

    def setUp(self):
        field = mock.MagicMock()
        field.notnull = True
        self.validator = fields.FieldValidator(field)

    def test_validate(self):
        self.assertRaises(NotImplementedError, self.validator.validate, 10)

    def test_validate_notnull(self):
        self.assertRaises(errors.ValidationError, self.validator.validate, None)

    def test_validate_notset(self):
        self.assertEqual(self.validator.validate(fields.NotSet), fields.NotSet)

    def test_validate_with_nullable_field(self):
        field = mock.MagicMock()
        field.notnull = False
        validator_nullable = fields.FieldValidator(field)
        self.assertEqual(validator_nullable.validate(None), None)

    def test_type_validation(self):
        self.assertRaises(NotImplementedError, self.validator.type_validation, 10)

    def test_validate_returns_value(self):
        def func(self, value):
            return value

        self.validator.type_validation = types.MethodType(func, self.validator)
        self.assertEqual(self.validator.validate(True), True)
        self.assertEqual(self.validator.validate(False), False)
        self.assertEqual(self.validator.validate(10), 10)


class TestCharValidator(TestCase):

    def setUp(self):
        char_field = mock.MagicMock(fields.CharField)
        char_field.max_length = 10
        char_field.notnull = True
        self.validator = fields.CharValidator(char_field)

    def test_type_validation(self):
        result = self.validator.type_validation('test1')
        self.assertEqual('test1', result)

    def test_int_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.type_validation, 1)

    def test_bool_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.type_validation, True)

    def test_date_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.type_validation, datetime.datetime)

    def test_max_length(self):
        self.assertRaises(errors.ValidationError, self.validator.type_validation, 'longer than 10 characters')


class TestIntValidator(TestCase):

    def setUp(self):
        self.validator = fields.IntValidator(mock.MagicMock())

    def test_type_validation(self):
        result = self.validator.type_validation(42)
        self.assertEqual(42, result)

    def test_long_validation(self):
        result = self.validator.type_validation(420000000000000000000000000)
        self.assertEqual(420000000000000000000000000, result)

    def test_str_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.type_validation, 'abc')

    def test_bool_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.type_validation, True)

    def test_date_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.type_validation, datetime.datetime)


class TestDateTimeValidator(TestCase):

    def setUp(self):
        self.validator = fields.DateTimeValidator(mock.MagicMock())

    def test_type_validation(self):
        dt = datetime.datetime.utcnow()
        result = self.validator.type_validation(dt)
        self.assertEqual(dt, result)

    def test_str_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.type_validation, 'abc')

    def test_bool_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.type_validation, True)

    def test_int_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.type_validation, 1)


class TestDecimalValidator(TestCase):

    def setUp(self):
        self.validator = fields.DecimalValidator(mock.MagicMock())

    def test_type_validation(self):
        result = self.validator.type_validation(4.2)
        self.assertEqual(4.2, result)

    def test_str_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.type_validation, 'abc')

    def test_bool_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.type_validation, True)

    def test_date_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.type_validation, datetime.datetime)


class TestBoolValidator(TestCase):

    def setUp(self):
        self.validator = fields.BoolValidator(mock.MagicMock())

    def test_type_validation(self):
        result = self.validator.type_validation(True)
        self.assertEqual(True, result)
        result = self.validator.type_validation(False)
        self.assertEqual(False, result)

    def test_str_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.type_validation, 'abc')

    def test_int_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.type_validation, 92)

    def test_date_invalid(self):
        self.assertRaises(errors.ValidationError, self.validator.type_validation, datetime.datetime)


class SimpleValidator(fields.FieldValidator):

    def validate(self, value):
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
        self.assertEqual(simple.notnull, False)
        self.assertEqual(simple.default, fields.NotSet)
        self.assertEqual(simple._value, fields.NotSet)

        with_default = SimpleTypedField(default=10)
        self.assertEqual(with_default.notnull, False)
        self.assertEqual(with_default.default, 10)
        self.assertEqual(with_default._value, 10)

        with_notnull = SimpleTypedField(notnull=True)
        self.assertEqual(with_notnull.notnull, True)
        self.assertEqual(with_notnull.default, fields.NotSet)
        self.assertEqual(with_notnull._value, fields.NotSet)

    def test_set_with_notset(self):
        self.assertEqual(self.field.set(fields.NotSet), fields.NotSet)
        self.assertEqual(self.field._value, fields.NotSet)

    def test_set_with_value(self):
        self.assertEqual(self.field.set(10), 10)
        self.assertEqual(self.field._value, 10)

    def test_set_calls_validator(self):
        self.field._validator = mock.MagicMock()
        self.field.set(10)
        self.field._validator.validate.assert_called_once_with(10)

    def test_get_with_value(self):
        self.field._value = 10
        self.assertEqual(self.field.get(), 10)

    def test_get_notset_with_default(self):
        self.assertEqual(self.field._value, fields.NotSet)
        self.field.default = 'abc'
        self.assertEqual(self.field.get(), fields.NotSet)

    def test_get_notset_without_default(self):
        self.assertEqual(self.field._value, fields.NotSet)
        self.assertEqual(self.field.default, fields.NotSet)
        self.assertEqual(self.field.get(), fields.NotSet)

    def test_to_default(self):
        self.field._value = 'abc'
        self.assertEqual(self.field.default, fields.NotSet)
        self.assertEqual(self.field.to_default(), fields.NotSet)
        self.assertEqual(self.field._value, fields.NotSet)

        self.field.default = 10
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
        self.assertEqual(self.field.max_length, None)
        self.field.set_unique_attributes(max_length=99)
        self.assertEqual(self.field.max_length, 99)

    def test_char_field_usage(self):
        self.assertEqual(self.field.set('hello world!'), self.field.get())

    def test_char_field_maxlength(self):
        self.field.max_length = 5
        self.assertRaises(errors.ValidationError, self.field.set, 'too long for max_length')

    def test_char_field_invalid_values(self):
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

    def test_char_field_usage(self):
        self.assertEqual(self.field.set(10), self.field.get())

    def test_char_field_invalid_values(self):
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

    def test_char_field_usage(self):
        self.assertEqual(self.field.set(True), self.field.get())

    def test_char_field_invalid_values(self):
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

    def test_char_field_usage(self):
        self.assertEqual(self.field.set(5.234), self.field.get())

    def test_char_field_invalid_values(self):
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

    def test_char_field_usage(self):
        self.assertEqual(self.field.set(datetime.datetime.utcnow()), self.field.get())

    def test_char_field_invalid_values(self):
        self.assertRaises(errors.ValidationError, self.field.set, 'abc')
        self.assertRaises(errors.ValidationError, self.field.set, 10)
        self.assertRaises(errors.ValidationError, self.field.set, True)


class TestCharParam(TestCase):

    def setUp(self):
        self.field = fields.CharParam()

    def test_inheritance(self):
        self.assertTrue(isinstance(self.field, fields.ResourceParam))

    def test_validator_type(self):
        self.assertEqual(self.field.validator_type, fields.CharValidator)

    def test_set_unique_attributes(self):
        self.assertEqual(self.field.max_length, None)
        self.field.set_unique_attributes(max_length=99)
        self.assertEqual(self.field.max_length, 99)

    def test_char_param_usage(self):
        self.assertEqual(self.field.set('hello world!'), self.field.get())

    def test_char_param_maxlength(self):
        self.field.max_length = 5
        self.assertRaises(errors.ValidationError, self.field.set, 'too long for max_length')

    def test_char_field_invalid_values(self):
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

    def test_char_field_usage(self):
        self.assertEqual(self.field.set(10), self.field.get())

    def test_char_field_invalid_values(self):
        self.assertRaises(errors.ValidationError, self.field.set, 'abc')
        self.assertRaises(errors.ValidationError, self.field.set, datetime.datetime.utcnow())
        self.assertRaises(errors.ValidationError, self.field.set, True)


class TestBoolParam(TestCase):

    def setUp(self):
        self.field = fields.BoolParam()

    def test_inheritance(self):
        self.assertTrue(isinstance(self.field, fields.ResourceParam))

    def test_validator_type(self):
        self.assertEqual(self.field.validator_type, fields.BoolValidator)

    def test_char_field_usage(self):
        self.assertEqual(self.field.set(True), self.field.get())

    def test_char_field_invalid_values(self):
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

    def test_char_field_usage(self):
        self.assertEqual(self.field.set(5.234), self.field.get())

    def test_char_field_invalid_values(self):
        self.assertRaises(errors.ValidationError, self.field.set, 'abc')
        self.assertRaises(errors.ValidationError, self.field.set, datetime.datetime.utcnow())
        self.assertRaises(errors.ValidationError, self.field.set, True)


class TestDateTimeParam(TestCase):

    def setUp(self):
        self.field = fields.DateTimeParam()

    def test_inheritance(self):
        self.assertTrue(isinstance(self.field, fields.ResourceParam))

    def test_validator_type(self):
        self.assertEqual(self.field.validator_type, fields.DateTimeValidator)

    def test_char_field_usage(self):
        self.assertEqual(self.field.set(datetime.datetime.utcnow()), self.field.get())

    def test_char_field_invalid_values(self):
        self.assertRaises(errors.ValidationError, self.field.set, 'abc')
        self.assertRaises(errors.ValidationError, self.field.set, 10)
        self.assertRaises(errors.ValidationError, self.field.set, True)