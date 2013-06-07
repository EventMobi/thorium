import json


class Dispatcher(object):

    def __init__(self, resource):
        self.resource = resource

    def dispatch(self, request):
        res = self.resource()

        if request.method == 'GET':
            res.engine.get()
            fields = res.get_field_dict()
            return json.dumps(fields)
        elif request.method == 'POST':
            res.engine.post()
        else:
            raise NotImplementedError
        return "asdf"


