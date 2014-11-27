from unittest import TestCase
from thorium import auth, errors


class SampleAuthenticator(auth.Authenticator):

    def _authenticate(self):
        return self.request

    def _authorize(self):
        return self.request

    @auth.validation
    def good_auth(self):
        return True

    @auth.validation
    def bad_auth(self):
        return False


@auth.use(SampleAuthenticator)
class SampleTestedClass(object):
    _authenticator_classes = None

    def __init__(self):
        self.request = True
        self.response = False
        self.auth = self._authenticator_classes[0](self)

    def method1(self):
        pass

    @SampleAuthenticator.no_auth
    def method2(self):
        pass

    @SampleAuthenticator.good_auth
    def method3(self):
        pass

    @SampleAuthenticator.bad_auth
    def method4(self):
        pass


class TestAuth(TestCase):

    def setUp(self):
        self.sample = SampleTestedClass()

    def test_bad_auth(self):
        self.sample.auth.request = False
        self.assertRaises(errors.UnauthorizedError, self.sample.auth.check_auth, self.sample.method1)

    def test_no_auth(self):
        self.sample.auth.request = False
        self.sample.auth.check_auth(self.sample.method2)

    def test_custom_auth_method(self):
        self.sample.auth.check_auth(self.sample.method3)

    def test_custom_auth_method_failure(self):
        self.assertRaises(errors.ForbiddenError, self.sample.auth.check_auth, self.sample.method4)



