import json


class Engine(object):

    def __init__(self, resource, request):
        self.resource = resource
        self.request = request

    def control(self):
        if self.request.method == 'GET':
            self.get()
            fields = self.resource.get_field_dict()
            return json.dumps(fields)
        elif self.request.method == 'POST':
            self.post()
        else:
            raise NotImplementedError

    def map(self, data_dict):
        for key, value in data_dict.items():
            self.resource.__setattr__(key, value)
