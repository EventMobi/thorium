from flask import jsonify, request
from flask.views import View
from thorium import fields


class Resource(View):

    def __init__(self):
        self.data = {'error': 'No data'}
        self.engine = self.Meta.engine(self)

    def dispatch_request(self):
        if request.method == 'GET':
            self.engine.get()
        elif request.method == 'POST':
            self.engine.post()

        dict = self.get_field_dict()
        return jsonify(**dict)

    def get_field_dict(self):
        """
        Pulls out all attributes with a base of ResourceField and
        returns a dict.
        """
        field_dict = {}
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if isinstance(attr, fields.ResourceField):
                field_dict[attr_name] = attr.value
        return field_dict