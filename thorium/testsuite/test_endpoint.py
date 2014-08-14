from unittest import TestCase, mock
from thorium import Endpoint, Request, auth, errors


class TestEndpoint(TestCase):

    def setUp(self):
        self.request = mock.MagicMock(spec=Request)
        self.response = mock.MagicMock(spec=Request)
        self.auth_cls = mock.MagicMock(spec=auth.Authenticator)
        Endpoint._authenticator_classes = [self.auth_cls]
        self.engine = Endpoint(self.request, self.response)

    def test_init(self):
        self.assertEqual(self.engine.request, self.request)
        self.auth_cls.assert_called_once_with(self.engine)

    def test_pre_request(self):
        self.engine.pre_request()

    def test_pre_request_detail(self):
        self.engine.pre_request_detail()

    def test_pre_request_collection(self):
        self.engine.pre_request_collection()

    def test_post_request(self):
        self.engine.post_request()

    def test_get_detail(self):
        self.assertRaises(errors.MethodNotImplementedError, self.engine.get_detail)

    def test_post_detail(self):
        self.assertRaises(errors.MethodNotImplementedError, self.engine.post_detail)

    def test_put_detail(self):
        self.assertRaises(errors.MethodNotImplementedError, self.engine.put_detail)

    def test_patch_detail(self):
        self.assertRaises(errors.MethodNotImplementedError, self.engine.patch_detail)

    def test_delete_detail(self):
        self.assertRaises(errors.MethodNotImplementedError, self.engine.delete_detail)

    def test_get_collection(self):
        self.assertRaises(errors.MethodNotImplementedError, self.engine.get_collection)

    def test_post_collection(self):
        self.assertRaises(errors.MethodNotImplementedError, self.engine.post_collection)

    def test_put_collection(self):
        self.assertRaises(errors.MethodNotImplementedError, self.engine.put_collection)

    def test_patch_collection(self):
        self.assertRaises(errors.MethodNotImplementedError, self.engine.patch_collection)

    def test_delete_collection(self):
        self.assertRaises(errors.MethodNotImplementedError, self.engine.delete_collection)
        
    def test_options(self):
        self.assertRaises(errors.MethodNotImplementedError, self.engine.options)

    def test_authenticate(self):
        auth_mock1 = mock.MagicMock(spec=auth.Authenticator)
        auth_mock2 = mock.MagicMock(spec=auth.Authenticator)
        self.engine._authenticators = [auth_mock1, auth_mock2]
        self.engine.authenticate('test')
        auth_mock1.check_auth.assert_called_once_with('test')
        auth_mock2.check_auth.assert_called_once_with('test')



