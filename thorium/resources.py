from . import errors, fields
import copy, collections

VALID_METHODS = {'get', 'post', 'put', 'patch', 'delete', 'options'}


class ResourceMetaClass(type):

    #Note: attrs comes in alphabetical order, unsure how to maintain declared order of fields
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
            for name, param in list(p_attrs.items()):
                if isinstance(param, fields.ResourceParam):
                    param.name = name
                    params[name] = param

        return params

    @staticmethod
    def _validate_format(mcs, resource_name, attrs):
        if 'Meta' in attrs:
            meta = attrs['Meta']

            detail = getattr(meta, 'detail', None)
            collection = getattr(meta, 'collection', None)

            detail_methods = detail['methods']
            if detail_methods:
                if not detail_methods.issubset(VALID_METHODS):
                    raise Exception('detail_methods: {dm} must be a subset of the '
                                    'valid methods: {VM}'.format(dm=detail_methods, VM=VALID_METHODS))
            else:
                detail['methods'] = set()
                setattr(meta, 'detail', detail)

            collection_methods = collection['methods'] or set()
            if collection_methods:
                if not collection_methods.issubset(VALID_METHODS):
                    raise Exception('collection_methods {cm} must be a subset of the '
                                    'valid methods: {VM}'.format(cm=collection_methods, VM=VALID_METHODS))
            else:
                collection['methods'] = set()
                setattr(meta, 'collection', collection)

            detail_endpoint = detail['endpoint']
            if not detail_endpoint:
                detail['endpoint'] = None
                setattr(meta, 'detail', detail)

            collection_endpoint = collection['endpoint']
            if not collection_endpoint:
                collection['endpoint'] = None
                setattr(meta, 'collection', collection)


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

    def from_obj(self, obj, mapping={}, explicit_mapping=False):
        """
        Maps the public attributes from a object to the resource fields based on identical names.
        Optional mapping parameter allows for discrepancies in naming with resource names being the
        key and the object attribute name to map to being the value. If explicit_mapping is True,
        only the attributes in the mapping dictionary will be copied.
        """
        if not explicit_mapping:
            obj_mapping_names = mapping.values()
            for name, field in self.all_fields():
                if name not in mapping and name not in obj_mapping_names and hasattr(obj, name):
                    val = getattr(obj, name)
                    field.set(val)

        for res_name, obj_name in mapping.items():
            if res_name and obj_name:
                val = getattr(obj, obj_name)
                self._fields[res_name].set(val)
        return self

    def to_obj(self, obj, mapping={}, explicit_mapping=False):
        """
        Maps the fields from the resource to an object based on identical names. Optional mapping
        parameter allows for discrepancies in naming with resource names being the
        key and the object attribute name to map to being the value. If explicit_mapping is True,
        only the attributes in the mapping dictionary will be copied.
        """
        if not explicit_mapping:
            for key in obj.__dict__:
                if not key.startswith('_') and key not in mapping and key in self._fields:
                    val = self._fields[key].get()
                    setattr(obj, key, val)

        for res_name, obj_name in mapping.items():
            if res_name and obj_name:
                val = self._fields[res_name].get()
                setattr(obj, obj_name, val)

        return obj

    def valid_fields(self):
        return ((name, field) for name, field in self._fields.items() if field.is_set())

    def all_fields(self):
        return ((name, field) for name, field in self._fields.items())

    def validate_full(self):
        for field in self._fields.values():
            if not field.is_set():
                raise errors.ValidationError('Field {0} is NotSet, expected full resource.'.format(field))