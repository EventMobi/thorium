import types
from unittest import TestCase, mock
from thorium import resources, fields, errors
import datetime

class SimpleResource(resources.Resource):
    name = fields.CharField()
    age = fields.IntField()


class SimpleObj(object):
    def __init__(self):
        self.name = None
        self.age = None
        self.extra = None


class TestSimpleResource(TestCase):

    def setUp(self):
        self.resource = SimpleResource()

    def test_from_dict(self):
        data = {
            'name': 'Fred',
            'age': 9001
        }
        self.resource.from_dict(data)
        self.assertEqual(self.resource.name, data['name'])
        self.assertEqual(self.resource.age, data['age'])

    def test_from_dict_invalid(self):
        data = {
            'name': 'Marvin',
            'age': '37 times older than the universe'
        }
        self.assertRaises(errors.ValidationError, self.resource.from_dict, data)

    def test_from_dict_extra_fields(self):
        data = {
            'name': 'Zaphod',
            'age': 42,
            'heads': 2
        }
        self.resource.from_dict(data)
        attribute_error = False
        try:
            self.resource.heads
        except AttributeError:
            attribute_error = True
        finally:
            self.assertTrue(attribute_error)

    def test_from_dict_partial(self):
        data = {
            'name': 'Fred'
        }
        self.resource.from_dict(data)
        self.assertEqual(self.resource.name, data['name'])
        self.assertEqual(self.resource.age, fields.NotSet)

    def test_to_dict(self):
        self.resource.name = 'Jack Daniel'
        self.resource.age = 24

        data = self.resource.to_dict()
        self.assertTrue(isinstance(data, dict))
        self.assertEqual(self.resource.name, data['name'])
        self.assertEqual(self.resource.age, data['age'])

        data2 = self.resource.to_dict()
        self.assertEqual(data, data2)

    def test_to_dict_partial(self):
        self.resource.name = 'Barney'
        data = self.resource.to_dict()
        self.assertTrue(isinstance(data, dict))
        self.assertEqual(self.resource.name, data['name'])
        self.assertNotIn('age', data)

    def test_valid_fields(self):
        self.resource.name = 'Arthur'
        valid_fields = self.resource.valid_fields()
        self.assertTrue(isinstance(valid_fields, types.GeneratorType))
        valid_fields = dict(valid_fields)
        self.assertIn('name', valid_fields)
        self.assertNotIn('age', valid_fields)
        self.assertEqual(valid_fields['name'].get(), 'Arthur')

    def test_valid_fields_with_defaults_is_not_set(self):
        self.resource.name = 'Trillian'
        self.resource._fields['age'].default = 0
        self.assertEqual(self.resource.age, fields.NotSet)
        valid_fields = self.resource.valid_fields()
        self.assertTrue(isinstance(valid_fields, types.GeneratorType))
        valid_fields = dict(valid_fields)
        self.assertIn('name', valid_fields)
        self.assertNotIn('age', valid_fields)
        self.assertEqual(valid_fields['name'].get(), 'Trillian')

    def test_resource_to_obj(self):
        self.resource.name = 'Marvin'
        self.resource.age = 9299992939
        so = self.resource.to_obj(SimpleObj())
        self.assertEqual(self.resource.name, so.name)
        self.assertEqual(self.resource.age, so.age)
        self.assertEqual(None, so.extra)

    def test_obj_to_resource(self):
        so = SimpleObj()
        so.name = 'Slartibartfast'
        so.age = 5000050
        self.resource.from_obj(so)

    def test_obj_to_resource_invalid(self):
        so = SimpleObj()
        so.name = 'somename'
        so.age = 'Not an age'
        self.assertRaises(errors.ValidationError, self.resource.from_obj, so)


class ComplexResource(resources.Resource):
    name = fields.CharField(max_length=20)
    age = fields.IntField()
    admin = fields.BoolField(default=True)
    birth_date = fields.DateTimeField()

    def __init__(self, extra=False):
        self.extra = extra


class ComplexObj(object):
    resource_mapping = {
        'admin': 'administrator',
        'birth_date': 'birth'
    }

    def __init__(self):
        self.name = None
        self.administrator = None
        self.birth = None
        self.somethingelse = None


class TestComplexResource(TestCase):

    def setUp(self):
        self.full = ComplexResource()
        self.partial = ComplexResource.partial()

    def test_full_resource_init(self):
        self.assertEqual(self.full.name, fields.NotSet)
        self.assertEqual(self.full.age, fields.NotSet)
        self.assertEqual(self.full.admin, True)
        self.assertEqual(self.full.birth_date, fields.NotSet)

    def test_partial_resource_init(self):
        self.assertEqual(self.partial.name, fields.NotSet)
        self.assertEqual(self.partial.age, fields.NotSet)
        self.assertEqual(self.partial.admin, fields.NotSet)
        self.assertEqual(self.partial.birth_date, fields.NotSet)

    def test_obj_to_resource_with_mapping(self):
        co = ComplexObj()
        co.name = 'Timmy!'
        co.administrator = False
        co.birth = datetime.datetime.now()
        co.somethingelse = 'abc'
        res = ComplexResource().from_obj(co, co.resource_mapping)
        self.assertEqual(res.name, co.name)
        self.assertEqual(res.admin, co.administrator)
        self.assertEqual(res.birth_date, co.birth)
        self.assertFalse(hasattr(res, 'somethingelse'))

    def test_resource_to_object_with_mapping(self):
        res = ComplexResource()
        co = self.full.to_obj(ComplexObj(), ComplexObj.resource_mapping)
        self.assertEqual(res.name, co.name)
        self.assertEqual(res.admin, co.administrator)
        self.assertEqual(res.birth_date, co.birth)

    def test_obj_to_resource_with_explicit_mapping(self):
        co = ComplexObj()
        co.name = 'Timmy!'
        co.administrator = False
        co.birth = datetime.datetime.now()
        co.somethingelse = 'abc'
        res = ComplexResource().from_obj(co, co.resource_mapping, explicit_mapping=True)
        self.assertNotEqual(res.name, co.name)
        self.assertEqual(res.name, fields.NotSet)
        self.assertEqual(res.admin, co.administrator)
        self.assertEqual(res.birth_date, co.birth)
        self.assertFalse(hasattr(res, 'somethingelse'))

    def test_resource_to_object_with_explicit_mapping(self):
        res = ComplexResource()
        co = self.full.to_obj(ComplexObj(), ComplexObj.resource_mapping, explicit_mapping=True)
        self.assertNotEqual(res.name, co.name)
        self.assertIsNone(co.name)
        self.assertEqual(res.admin, co.administrator)
        self.assertEqual(res.birth_date, co.birth)

