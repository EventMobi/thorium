class Dispatcher(object):

    def __init__(self, resource, engine):
        self.resource = resource
        self.engine = engine

    def dispatch(self, request):
        res = self.resource()
        eng = self.engine(resource=res, request=request)
        return eng.control()


