from unittest import TestCase
from thorium import params, Parameters


class SimpleParams(Parameters):
    name = params.CharParam(default=None)
    req = params.IntParam(notnull=True)


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
