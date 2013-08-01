from unittest import TestCase, mock
from thorium import resources, fields, errors


class SimpleResource(resources.Resource):
    name = fields.CharField()
    age = fields.IntField()


class TestResource(TestCase):

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

        validation_error = False
        try:
            age = self.resource.age
        except errors.ValidationError:
            validation_error = True
        finally:
            self.assertTrue(validation_error)

    def test_to_dict(self):
        self.resource.name = 'Jack Daniel'
        self.resource.age = 24

        data = self.resource.to_dict()
        self.assertEqual(self.resource.name, data['name'])
        self.assertEqual(self.resource.age, data['age'])

        data2 = self.resource.to_dict(False)
        self.assertEqual(data, data2)

    def test_to_dict_partial(self):
        self.resource.name = 'Barney'
        data = self.resource.to_dict(True)
        self.assertEqual(self.resource.name, data['name'])
        self.assertNotIn('age', data)

    def test_to_dict_incomplete_data(self):
        self.resource.name = 'Marvin'
        validation_error = False
        try:
            data = self.resource.to_dict(False)
        except errors.ValidationError:
            validation_error = True
        finally:
            self.assertTrue(validation_error)

    def test_valid_fields(self):
        self.resource.name = 'Arthur'
        valid_fields = self.resource.valid_fields()
        self.assertIn('name', valid_fields)
        self.assertNotIn('age', valid_fields)
        self.assertEqual(valid_fields['name'].get(), 'Arthur')

    def test_valid_fields_with_defaults_is_not_set(self):
        self.resource.name = 'Trillian'
        self.resource._fields['age'].default = 0
        self.assertEqual(self.resource.age, 0)
        valid_fields = self.resource.valid_fields()
        self.assertIn('name', valid_fields)
        self.assertNotIn('age', valid_fields)
        self.assertEqual(valid_fields['name'].get(), 'Trillian')




