from unittest import TestCase
from thorium import params, Parameters, errors


class SimpleParams(Parameters):
    name = params.CharParam(default=None)
    req = params.IntParam(notnull=True)
    tags = params.JSONParam()
    schema_test = params.JSONParam(schema={
        'type': 'object',
        'properties':{
            'string': {'type': 'string'},
            'number': {'type': 'number'}
        }
    })


class TestSimpleParams(TestCase):

    def setUp(self):
        self.test_data = {'name': 'abc', 'req': 10}

    def test_validate(self):
        result = SimpleParams.validate(self.test_data)
        self.assertEqual(result, self.test_data)

    def test_validate_default(self):
        expected = {'name': None, 'req': 10}
        result = SimpleParams.validate({'req': 10})
        self.assertEqual(result, expected)

    def test_validate_required_param(self):
        result = SimpleParams.validate({'name': 'abd'})

    def test_validate_valid_json(self):
        result = SimpleParams.validate({
            'tags': '{"new":true, "id": 1}'
        })
        self.assertTrue(result['tags']['new'])
        self.assertEqual(result['tags']['id'], 1)

    def test_validate_invalid_json(self):
        data = { 'tags': '{new:true, id_invalid: \'1\'}' }
        self.assertRaises(errors.ValidationError, SimpleParams.validate, data)

    def test_schema_json_valid(self):
        result = SimpleParams.validate({
            'schema_test': '{"string":"hi", "number": 1}'
        })

        self.assertEqual(result['schema_test']['string'], 'hi')
        self.assertEqual(result['schema_test']['number'], 1)

    def test_schema_json_invalid(self):
        data = {
            'schema_test': '{"string":1, "number": 2}'
        }

        self.assertRaises(errors.ValidationError, SimpleParams.validate, data)
