from thorium import DetailResourceInterface, CollectionResourceInterface, fields
from thorium.testsuite.helpers.commonhelper import Stub
from thorium.testsuite.helpers import enginehelper


class ResourceStub(Stub):

    def __init__(self):
        super(ResourceStub, self).__init__(DetailResourceInterface)


class TestResourceInterface(DetailResourceInterface):
    name = fields.CharField()
    birth_date = fields.DateTimeField()
    age = fields.IntField()
    admin = fields.BoolField()

    class Meta:
        endpoint = '/testapi/testresource/<int:id>'
        methods = ['GET', 'POST']
        engine = enginehelper.EngineStub


class TestResourceInterface2(DetailResourceInterface):
    name = fields.CharField()
    birth_date = fields.DateTimeField()
    age = fields.IntField()
    admin = fields.BoolField()

    class Meta:
        endpoint = '/testapi/testresource/<int:id>'
        methods = ['GET', 'POST']
        engine = enginehelper.TestEngine


class TestResourceInterface3(CollectionResourceInterface):
    name = fields.CharField()
    birth_date = fields.DateTimeField()
    age = fields.IntField()
    admin = fields.BoolField()

    class Meta:
        endpoint = '/testapi/testresource'
        methods = ['GET', 'POST']
        engine = enginehelper.TestEngine2


