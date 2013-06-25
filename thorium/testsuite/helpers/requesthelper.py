from thorium.testsuite.helpers.commonhelper import Stub
from thorium import Request


class RequestStub(Stub):

    def __init__(self):
        super(RequestStub, self).__init__(Request)


def get_test_request(method):
    return Request(method=method, identifiers={}, resource=None, query_params=None)