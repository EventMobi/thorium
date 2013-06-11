import fields
import routing
from dispatcher import Dispatcher


def endpoint(path):
    def _register_endpoint(resource):
        dsp = Dispatcher(resource, resource.Meta.engine)
        route = routing.Route(resource.__name__, path, dsp)
        routing.add_route(route)
    return _register_endpoint


class Resource(object):

    def __init__(self):
        pass

    def __setattr__(self, name, value):
        field = getattr(self, name)
        if isinstance(field, fields.ResourceField):
            field.set(value)
        else:
            raise Exception('Can only assign to Fields')

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


