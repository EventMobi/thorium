from unittest import TestCase
from thorium import Engine, Request
from thorium.testsuite.helpers import resourcehelper, requesthelper
from thorium.testsuite.helpers.commonhelper import ReachedMethod
from datetime import date
import calendar


class TestEngine(TestCase):

    def setUp(self):
        self.res = resourcehelper.TestResourceInterface()

        self.req = None
        try:
            self.req = requesthelper.RequestStub()
        except ReachedMethod as reached_method:
            self.assertTrue(reached_method.expected(Request.__init__))

        self.engine = Engine(self.req)

    def test_init(self):
        self.assertEqual(self.engine.request, self.req)

    def test_pre_request(self):
        self.engine.pre_request()
        self.assertTrue(True)

    def test_post_request(self):
        self.engine.post_request()
        self.assertTrue(True)

    def test_get(self):
        self.assertRaises(NotImplementedError, self.engine.get)

    def test_post(self):
        self.assertRaises(NotImplementedError, self.engine.post)

    def test_put(self):
        self.assertRaises(NotImplementedError, self.engine.put)

    def test_patch(self):
        self.assertRaises(NotImplementedError, self.engine.patch)

    def test_delete(self):
        self.assertRaises(NotImplementedError, self.engine.delete)

    def test_options(self):
        self.assertRaises(NotImplementedError, self.engine.options)




