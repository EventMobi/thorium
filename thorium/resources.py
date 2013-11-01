from . import errors, fields
import copy, collections

VALID_METHODS = {'get', 'post', 'put', 'patch', 'delete', 'options'}


class ResourceMetaClass(type):

    #Note: attrs comes in alphabetical order, unsure how to maintain declared order of fields
    def __new__(mcs, resource_name, bases, attrs):

        # validate Resource's children but not Resource
        #if resource_name != 'Resource':
        #    mcs._validate_format(mcs, resource_name, attrs)

        attrs['_fields'] = mcs._get_fields(bases, attrs)
        attrs['query_parameters'] = mcs._get_params(attrs)
        return super().__new__(mcs, resource_name, bases, attrs)

    #Note: will likely need some sort of sorted dictionary to maintain field order
    @staticmethod
    def _get_fields(bases, attrs):

        # gather fields to add to _fields dictionary
        # also replaces field definition with a property to wrap the _fields dictionary
        field_dict = collections.OrderedDict()
        for name, field in attrs.items():
            if isinstance(field, fields.ResourceField):
                field.name = name
                field_dict[name] = field
                attrs[name] = property(fget=ResourceMetaClass._gen_get_prop(name),
                                       fset=ResourceMetaClass._get_set_prop(name))

        return field_dict

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
            params = {name: param for name, param in list(p_attrs.items()) if isinstance(param, fields.ResourceParam)}
        return params

    @staticmethod
    def _validate_format(mcs, resource_name, attrs):
        if 'Meta' in attrs:
            meta = attrs['Meta']

            detail_methods = getattr(meta, 'detail_methods', None)
            if detail_methods:
                if not detail_methods.issubset(VALID_METHODS):
                    raise Exception('detail_methods: {dm} must be a subset of the '
                                    'valid methods: {VM}'.format(dm=detail_methods, VM=VALID_METHODS))
            else:
                setattr(meta, 'detail_methods', set())

            collection_methods = getattr(meta, 'collection_methods', None) or set()
            if collection_methods:
                if not collection_methods.issubset(VALID_METHODS):
                    raise Exception('collection_methods {cm} must be a subset of the '
                                    'valid methods: {VM}'.format(cm=collection_methods, VM=VALID_METHODS))
            else:
                setattr(meta, 'collection_methods', set())

            detail_endpoint = getattr(meta, 'detail_endpoint', None)
            if not detail_endpoint:
                setattr(meta, 'detail_endpoint', None)

            collection_endpoint = getattr(meta, 'collection_endpoint', None)
            if not collection_endpoint:
                setattr(meta, 'collection_endpoint', None)


class Resource(object, metaclass=ResourceMetaClass):

    def __new__(cls, *args):
        obj = super().__new__(cls, *args)
        obj._fields = copy.deepcopy(obj._fields)
        return obj

    @classmethod
    def partial(cls, *args, **kwargs):
        obj = cls(*args, **kwargs)
        for field in obj._fields.values():
            field.set(fields.NotSet)
        return obj

    def from_dict(self, data):
        for name, field in self._fields.items():
            if name in data:
                field.set(data[name])

    def to_dict(self):
        return {name: field.get() for name, field in self.valid_fields()}

    def valid_fields(self):
        return ((name, field) for name, field in self._fields.items() if field.is_set())

    def all_fields(self):
        return ((name, field) for name, field in self._fields.items())

    def validate_full(self):
        for field in self._fields.values():
            if not field.is_set():
                raise errors.ValidationError('Field {0} is NotSet, expected full resource.'.format(field))