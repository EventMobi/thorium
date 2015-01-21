import types
from unittest import TestCase
from thorium import resources, fields, errors, NotSet
import datetime


class SimpleResource(resources.Resource):
    name = fields.CharField(default=None)
    age = fields.IntField(default=None)
    readonly = fields.IntField(readonly=True)
    not_mutable = fields.IntField(mutable=False, default=0)


class SimpleObj(object):
    def __init__(self):
        self.name = None
        self.age = None
        self.extra = None
        self.not_mutable = None


class TestSimpleResource(TestCase):

    def setUp(self):
        self.resource = SimpleResource()

    def test_from_dict(self):
        data = {
            'name': 'Fred',
            'age': 9001,
            'readonly': 10,
            'not_mutable': 0
        }
        self.resource.from_dict(data)
        self.assertEqual(self.resource.name, data['name'])
        self.assertEqual(self.resource.age, data['age'])
        self.assertEqual(self.resource.readonly, data['readonly'])
        self.assertEqual(self.resource.not_mutable, data['not_mutable'])

    def test_from_dict_invalid(self):
        data = {
            'name': 'Marvin',
            'age': '37 times older than the universe'
        }
        self.assertRaises(errors.ValidationError, self.resource.from_dict, data)

        data = {
            'not_mutable': 123
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
        self.assertEqual(self.resource.age, None)
        self.assertEqual(self.resource.not_mutable, 0)

    def test_to_dict(self):
        self.resource.name = 'Jack Daniel'
        self.resource.age = 24

        data = self.resource.to_dict()
        self.assertTrue(isinstance(data, dict))
        self.assertEqual(self.resource.name, data['name'])
        self.assertEqual(self.resource.age, data['age'])
        self.assertEqual(self.resource.not_mutable, data['not_mutable'])

        data2 = self.resource.to_dict()
        self.assertEqual(data, data2)

    def test_to_dict_partial(self):
        res = SimpleResource.partial(name='Barney')
        data = res.to_dict()
        self.assertTrue(isinstance(data, dict))
        self.assertEqual(res.name, data['name'])
        self.assertNotIn('age', data)
        self.assertNotIn('not_mutable', data)

    def test_valid_fields(self):
        res = SimpleResource.partial(name='Arthur')
        valid_fields = res.valid_fields()
        self.assertTrue(isinstance(valid_fields, types.GeneratorType))
        valid_fields = dict(valid_fields)
        self.assertIn('name', valid_fields)
        self.assertNotIn('age', valid_fields)
        self.assertNotIn('not_mutable', valid_fields)
        self.assertEqual(dict(res.items())['name'], 'Arthur')

    def test_valid_fields_with_defaults_is_not_set(self):
        res = SimpleResource.partial(name='Trillian')
        dict(res.all_fields())['age'].flags['default'] = 0
        self.assertEqual(res.age, NotSet)
        self.assertEqual(res.not_mutable, NotSet)
        valid_fields = res.valid_fields()
        self.assertTrue(isinstance(valid_fields, types.GeneratorType))
        valid_fields = dict(valid_fields)
        self.assertIn('name', valid_fields)
        self.assertNotIn('age', valid_fields)
        self.assertNotIn('not_mutable', valid_fields)
        self.assertEqual(dict(res.items())['name'], 'Trillian')

    def test_to_default(self):
        res = SimpleResource.partial(name='Aristotle')
        self.assertEqual(res._values['name'], 'Aristotle')
        self.assertEqual(res.name, 'Aristotle')
        res.to_default('name')
        self.assertEqual(res._values['name'], None)
        self.assertEqual(res.name, None)

    def test_to_default_invalid(self):
        res = SimpleResource.partial(not_mutable=123)
        self.assertEqual(res._values['not_mutable'], 123)
        self.assertEqual(res.not_mutable, 123)
        self.assertRaises(errors.ValidationError, res.to_default, 'not_mutable')

    def test_items(self):
        data = {
            'name': 'Bob',
            'age': 401,
            'readonly': 1,
            'not_mutable': 0
        }
        self.resource.from_dict(data)
        items = self.resource.items()
        items = dict(items)
        self.assertDictEqual(items, data)

    def test_resource_to_obj(self):
        self.resource.name = 'Marvin'
        self.resource.age = 9299992939
        so = self.resource.to_obj(SimpleObj())
        self.assertEqual(self.resource.name, so.name)
        self.assertEqual(self.resource.age, so.age)
        self.assertEqual(None, so.extra)
        self.assertEqual(self.resource.not_mutable, so.not_mutable)

    def test_obj_to_resource(self):
        so = SimpleObj()
        so.name = 'Slartibartfast'
        so.age = 5000050
        so.not_mutable = 0
        self.resource.from_obj(so)
        self.assertEqual(self.resource.name, so.name)
        self.assertEqual(self.resource.age, so.age)
        self.assertEqual(self.resource.not_mutable, so.not_mutable)

    def test_obj_to_resource_invalid(self):
        so = SimpleObj()
        so.name = 'somename'
        so.age = 'Not an age'
        self.assertRaises(errors.ValidationError, self.resource.from_obj, so)

        so.not_mutable = 123
        self.assertRaises(errors.ValidationError, self.resource.from_obj, so)

    def test_seperate_resource_instsances_do_not_share_data(self):
        s1 = SimpleResource(name='a')
        s2 = SimpleResource(name='b')
        self.assertEqual(s1.name, 'a')


class ComplexResource(resources.Resource):
    name = fields.CharField(max_length=20)
    age = fields.IntField()
    admin = fields.BoolField(default=True)
    birth_date = fields.DateTimeField(mutable=False)


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
        self.data = {'name': 'Socrates', 'age': 71, 'admin': True, 'birth_date': datetime.datetime.now()}
        self.full = ComplexResource(self.data)
        self.partial = ComplexResource.partial()

    def test_dict_init(self):
        data = {'name': 'Socrates', 'age': 71, 'admin': True, 'birth_date': datetime.datetime.now()}
        res = ComplexResource(data)
        self.assertEqual(res.name, data['name'])
        self.assertEqual(res.age, data['age'])
        self.assertEqual(res.admin, data['admin'])
        self.assertEqual(res.birth_date, data['birth_date'])

    def test_keyword_init(self):
        data = {'name': 'Socrates', 'age': 71, 'admin': True, 'birth_date': datetime.datetime.now()}
        res = ComplexResource(name=data['name'], age=data['age'], admin=data['admin'], birth_date=data['birth_date'])
        self.assertEqual(res.name, data['name'])
        self.assertEqual(res.age, data['age'])
        self.assertEqual(res.admin, data['admin'])
        self.assertEqual(res.birth_date, data['birth_date'])

    def test_keyword_init_overrides_dict(self):
        data = {'name': 'Socrates', 'age': 71, 'admin': True, 'birth_date': datetime.datetime.now()}
        res = ComplexResource(data, age=30, admin=False)
        self.assertEqual(res.name, data['name'])
        self.assertEqual(res.age, 30)
        self.assertEqual(res.admin, False)
        self.assertEqual(res.birth_date, data['birth_date'])

    def test_resource_init_empty_full(self):
        res = ComplexResource.empty()
        self.assertEqual(res.name, None)
        self.assertEqual(res.age, None)
        self.assertEqual(res.admin, True)
        self.assertEqual(res.birth_date, NotSet)

    def test_resource_init_from_obj_full(self):
        co = ComplexObj()
        co.name = 'Timmy!'
        co.administrator = False
        co.birth = datetime.datetime.now()
        co.somethingelse = 'abc'
        self.assertRaises(errors.ValidationError, ComplexResource.init_from_obj, co)

    def test_resource_init_from_obj_full_with_mapping(self):
        co = ComplexObj()
        co.name = 'Timmy!'
        co.administrator = False
        co.birth = datetime.datetime.now()
        co.somethingelse = 'abc'
        co.age = 29
        res = ComplexResource.init_from_obj(co, mapping=co.resource_mapping)
        self.assertEqual(res.name, co.name)
        self.assertEqual(res.age, co.age)
        self.assertEqual(res.admin, co.administrator)
        self.assertEqual(res.birth_date, co.birth)

    def test_resource_init_from_obj_full_with_override(self):
        co = ComplexObj()
        co.name = 'Timmy!'
        co.administrator = False
        co.birth = datetime.datetime.now()
        co.somethingelse = 'abc'
        res = ComplexResource.init_from_obj(co, override={'admin': co.administrator, 'birth_date': co.birth, 'age': 29})
        self.assertEqual(res.name, co.name)
        self.assertEqual(res.age, 29)
        self.assertEqual(res.admin, co.administrator)
        self.assertEqual(res.birth_date, co.birth)

    def test_resource_init_from_obj_full_with_mapping_and_override(self):
        co = ComplexObj()
        co.name = 'Timmy!'
        co.administrator = False
        co.birth = datetime.datetime.now()
        co.somethingelse = 'abc'
        res = ComplexResource.init_from_obj(co,
                                            mapping=co.resource_mapping,
                                            override={'administrator': co.administrator, 'birth': co.birth, 'age': 29})
        self.assertEqual(res.name, co.name)
        self.assertEqual(res.age, 29)
        self.assertEqual(res.admin, co.administrator)
        self.assertEqual(res.birth_date, co.birth)

    def test_resource_init_from_obj_partial(self):
        co = ComplexObj()
        co.name = 'Timmy!'
        co.administrator = False
        co.birth = datetime.datetime.now()
        co.somethingelse = 'abc'
        res = ComplexResource.init_from_obj(co, partial=True)
        self.assertEqual(res.name, co.name)
        self.assertEqual(res.age, NotSet)
        self.assertEqual(res.admin, NotSet)
        self.assertEqual(res.birth_date, NotSet)

    def test_resource_init_from_obj_partial_with_mapping(self):
        co = ComplexObj()
        co.name = 'Timmy!'
        co.administrator = False
        co.birth = datetime.datetime.now()
        co.somethingelse = 'abc'
        res = ComplexResource.init_from_obj(obj=co, partial=True, mapping=co.resource_mapping)
        self.assertEqual(res.name, co.name)
        self.assertEqual(res.age, NotSet)
        self.assertEqual(res.admin, co.administrator)
        self.assertEqual(res.birth_date, co.birth)

    def test_resource_init_from_obj_partial_with_override(self):
        co = ComplexObj()
        co.name = 'Timmy!'
        co.administrator = False
        co.birth = datetime.datetime.now()
        co.somethingelse = 'abc'
        res = ComplexResource.init_from_obj(obj=co, partial=True, override={'age': 29, 'admin': False})
        self.assertEqual(res.name, co.name)
        self.assertEqual(res.age, 29)
        self.assertEqual(res.admin, False)
        self.assertEqual(res.birth_date, NotSet)

    def test_resource_init_from_obj_partial_with_mapping_and_override(self):
        co = ComplexObj()
        co.name = 'Timmy!'
        co.administrator = False
        co.birth = datetime.datetime.now()
        co.somethingelse = 'abc'
        res = ComplexResource.init_from_obj(obj=co,
                                            partial=True,
                                            mapping=co.resource_mapping,
                                            override={'age': 29, 'admin': False})
        self.assertEqual(res.name, co.name)
        self.assertEqual(res.age, 29)
        self.assertEqual(res.admin, False)
        self.assertEqual(res.birth_date, co.birth)

    def test_full_resource_must_be_valid(self):
        self.assertRaises(errors.ValidationError, setattr, self.full, 'name', NotSet)
        self.assertRaises(errors.ValidationError, setattr, self.full, 'age', NotSet)
        self.assertRaises(errors.ValidationError, setattr, self.full, 'admin', NotSet)
        self.assertRaises(errors.ValidationError, setattr, self.full, 'birth_date', NotSet)

        data = {'name': 'Socrates', 'age': 71, 'admin': NotSet, 'birth_date': datetime.datetime.now()}
        self.assertRaises(errors.ValidationError, ComplexResource, data)
        self.assertRaises(errors.ValidationError, self.full.from_dict, data)

    def test_full_resource_empty_init_fails(self):
        self.assertRaises(errors.ValidationError, ComplexResource)

    def test_partial_resource_empty_init(self):
        self.assertTrue(ComplexResource.partial())

    def test_partial_resource_allows_notset(self):
        self.partial.age = 14
        self.partial.age = NotSet
        self.assertEqual(self.partial.age, NotSet)

        data = {'name': 'Socrates', 'age': 71, 'admin': NotSet, 'birth_date': datetime.datetime.now()}
        self.partial.from_dict(data)
        self.assertEqual(self.partial.admin, NotSet)
        self.assertEqual(self.partial.age, 71)

        res = ComplexResource.partial(data)
        self.assertEqual(res.admin, NotSet)
        self.assertEqual(res.age, 71)

    def test_partial_resource_init(self):
        self.assertEqual(self.partial.name, NotSet)
        self.assertEqual(self.partial.age, NotSet)
        self.assertEqual(self.partial.admin, NotSet)
        self.assertEqual(self.partial.birth_date, NotSet)

    def test_obj_to_resource_with_mapping(self):
        co = ComplexObj()
        co.name = 'Timmy!'
        co.administrator = False
        co.birth = datetime.datetime.now()
        co.somethingelse = 'abc'
        co.age = 30
        res = ComplexResource.empty().from_obj(co, co.resource_mapping)
        self.assertEqual(res.name, co.name)
        self.assertEqual(res.admin, co.administrator)
        self.assertEqual(res.birth_date, co.birth)
        self.assertFalse(hasattr(res, 'somethingelse'))

    def test_obj_to_resource_with_override(self):
        co = ComplexObj()
        co.name = 'Timmy!'
        co.administrator = False
        co.birth = datetime.datetime.now()
        co.somethingelse = 'abc'
        res = ComplexResource.empty().from_obj(obj=co,
                                               override={'admin': co.administrator, 'birth_date': co.birth, 'age': 30})
        self.assertEqual(res.age, 30)
        self.assertEqual(res.name, co.name)
        self.assertEqual(res.admin, co.administrator)
        self.assertEqual(res.birth_date, co.birth)
        self.assertFalse(hasattr(res, 'somethingelse'))

    def test_obj_to_resource_with_override_and_mapping(self):
        co = ComplexObj()
        co.name = 'Timmy!'
        co.administrator = False
        co.birth = datetime.datetime.now()
        co.somethingelse = 'abc'
        res = ComplexResource.empty().from_obj(obj=co,
                                               mapping=co.resource_mapping,
                                               override={'age': 29, 'admin': False})
        self.assertEqual(res.name, co.name)
        self.assertEqual(res.admin, False)
        self.assertEqual(res.age, 29)
        self.assertEqual(res.birth_date, co.birth)
        self.assertFalse(hasattr(res, 'somethingelse'))

    def test_resource_to_object_with_mapping(self):
        co = self.full.to_obj(ComplexObj(), ComplexObj.resource_mapping)
        self.assertEqual(self.full.name, co.name)
        self.assertEqual(self.full.admin, co.administrator)
        self.assertEqual(self.full.birth_date, co.birth)

    def test_resource_to_object_not_mutable_field(self):
        co = ComplexObj()
        co.birth = datetime.datetime(1995, 1, 1)
        self.assertRaises(errors.BadRequestError,
                          self.full.to_obj,
                          co, co.resource_mapping)
