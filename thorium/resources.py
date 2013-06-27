from .fields import ResourceField, ResourceParam
import copy
from itertools import chain

VALID_METHODS = {'get', 'post', 'put', 'patch', 'delete'}


class ResourceMetaClass(type):
    def __new__(mcs, resource_name, bases, attrs):

        # validate Resource's children but not Resource
        if resource_name != 'Resource':
            mcs._validate_format(mcs, resource_name, attrs)

        attrs['_fields'] = mcs._get_fields(bases, attrs)
        attrs['query_parameters'] = mcs._get_params(attrs)
        return super().__new__(mcs, resource_name, bases, attrs)

    #Note: will likely need some sort of sorted dictionary to maintain field order
    @staticmethod
    def _get_fields(bases, attrs):

        # gather fields to add to _fields dictionary
        # also replaces field definition with a property to wrap the _fields dictionary
        fields = {}
        for name, field in attrs.items():
            if isinstance(field, ResourceField):
                fields[name] = field
                attrs[name] = property(fget=ResourceMetaClass._gen_get_prop(name),
                                       fset=ResourceMetaClass._get_set_prop(name))

        # append fields in bases
        for base in bases[::-1]:
            if hasattr(base, '_fields'):
                fields = dict(chain(base._fields.items(), fields.items()))

        return fields

    @staticmethod
    def _gen_get_prop(name):
        def get_field_property(self):
            return self._fields[name].get()
        return get_field_property

    @staticmethod
    def _get_set_prop(name):
        def set_field_property(self, value):
            return self._fields[name].set(value)
        return set_field_property

    @staticmethod
    def _get_params(attrs):
        params = {}
        if 'Params' in attrs:
            p_attrs = attrs.pop('Params').__dict__
            params = {name: param for name, param in list(p_attrs.items()) if isinstance(param, ResourceParam)}
        return params

    @staticmethod
    def _validate_format(mcs, resource_name, attrs):

        if not 'Meta' in attrs:
            raise Exception('Meta class must be present.')

        meta = attrs['Meta']

        mcs._get_required_attribute(resource_name, meta, 'detail_endpoint')
        mcs._get_required_attribute(resource_name, meta, 'collection_endpoint')

        detail_methods = mcs._get_required_attribute(resource_name, meta, 'detail_methods')
        if not detail_methods.issubset(VALID_METHODS):
            raise Exception('detail_methods: {dm} must be a subset of the '
                            'valid methods: {VM}'.format(dm=detail_methods, VM=VALID_METHODS))

        collection_methods = mcs._get_required_attribute(resource_name, meta, 'collection_methods')
        if not collection_methods.issubset(VALID_METHODS):
            raise Exception('collection_methods {cm} must be a subset of the '
                            'valid methods: {VM}'.format(cm=collection_methods, VM=VALID_METHODS))

        engine = mcs._get_required_attribute(resource_name, meta, 'engine')

    @staticmethod
    def _get_required_attribute(resource_name, meta, attr_name):
        attr = getattr(meta, attr_name, None)
        if not attr:
            raise Exception('Required attribute {at_n} not found '
                            'in the {rs_n} Resource\'s Meta class.'.format(at_n=attr_name, rs_n=resource_name))
        return attr


class Resource(object, metaclass=ResourceMetaClass):

    def __init__(self):
        # create copy of fields for this instance
        self._fields = copy.deepcopy(self._fields)

    def from_dict(self, data, convert=False):
        for name, field in self._fields.items():
            if name in data:
                field.set(data[name], convert)

    def to_dict(self, partial=False):
        if partial:
            fields = self.valid_fields()
        else:
            fields = self._fields

        return {name: field.get() for name, field in fields.items()}

    def valid_fields(self):
        return {name: field for name, field in self._fields.items() if field.is_set()}


class ResourceManager(object):
    """ Manages :class:`.Resource` objects. """

    def __init__(self, resource_cls):
        self.resource_cls = resource_cls

    def get_parameters(self, input_params):
        """ Returns a name to :class:`.ResourceParam` dictionary. """
        param_dict = self._get_params()
        for name, param in param_dict.items():
            param.set(input_params[name], convert=True) if name in input_params else param.to_default()
        return param_dict

    def _get_params(self):
        """ Creates a new dictionary of query parameters from the resource. """
        return copy.deepcopy(self.resource_cls.query_parameters)