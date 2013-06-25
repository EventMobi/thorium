from thorium import Engine
from thorium.testsuite.helpers.commonhelper import Stub
from datetime import date


class EngineStub(Stub):

    def __init__(self, *args, **kwargs):
        super(EngineStub, self).__init__(Engine, pass_methods=['__init__', 'pre_request', 'post_request'])


class TestEngine(Engine):

    def get(self):
        data = {
            'name': 'Timmy',
            'birth_date': date(2012, 3, 13),
            'age': 1,
            'admin': True
        }
        return data


class TestEngine2(Engine):

    def get(self):
        data = [{
            'name': 'Timmy',
            'birth_date': date(2012, 3, 13),
            'age': 1,
            'admin': True
        }]
        return data
