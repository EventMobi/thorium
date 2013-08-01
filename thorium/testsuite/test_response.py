from unittest import TestCase, mock
from thorium.response import Response, DetailResponse, CollectionResponse


class TestResponse(TestCase):

    def setUp(self):
        self.request_mock = mock.MagicMock()
        self.response = Response(request=self.request_mock)

    def test_location_header(self):
        self.request_mock.url = 'http://testurl/api'
        self.response.location_header(10)
        self.assertEqual(self.response.headers['Location'], 'http://testurl/api/10')


class TestDetailResponse(TestCase):

    def setUp(self):
        self.request_mock = mock.MagicMock()
        self.response = DetailResponse(request=self.request_mock)

    def test_set_resource_from_dict(self):
        data = {'a': 4}
        result = self.response.set_resource_from_dict(data)
        self.request_mock.resource_cls.assert_called_once_with()
        self.response.resource.from_dict.assert_called_once_with(data)
        self.assertEqual(result, self.response.resource)


class TestCollectionResponse(TestCase):

    def setUp(self):
        self.request_mock = mock.MagicMock()
        self.response = CollectionResponse(request=self.request_mock)

    def test_add_resource_from_dict(self):
        data = {'a': 4}
        result = self.response.add_resource_from_dict(data)
        self.request_mock.resource_cls.assert_called_once_with()
        self.response.resources[0].from_dict.assert_called_once_with(data)
        self.assertEqual(result, self.response.resources[0])