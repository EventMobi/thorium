from . import errors, fields
import copy
import collections

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

        #Sort the dictionary by order value.
        sorted_dict = collections.OrderedDict(sorted(field_dict.items(), key=lambda x: x[1].order_value))
        return sorted_dict

    @staticmethod
    def _gen_get_prop(name):
        def get_field_property(self):
            return self._fields[name].get()
        return get_field_property

    @staticmethod
    def _get_set_prop(name):
        def set_field_property(self, value):
            return self._set(self._fields[name], value)
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

            detail = getattr(meta, 'detail', {})
            collection = getattr(meta, 'collection', {})

            detail_methods = detail.get('methods')
            if detail_methods:
                if not detail_methods.issubset(VALID_METHODS):
                    raise Exception('detail_methods: {dm} must be a subset of the '
                                    'valid methods: {VM}'.format(dm=detail_methods, VM=VALID_METHODS))
            else:
                detail['methods'] = set()
                setattr(meta, 'detail', detail)

            collection_methods = collection.get('methods')
            if collection_methods:
                if not collection_methods.issubset(VALID_METHODS):
                    raise Exception('collection_methods {cm} must be a subset of the '
                                    'valid methods: {VM}'.format(cm=collection_methods, VM=VALID_METHODS))
            else:
                collection['methods'] = set()
                setattr(meta, 'collection', collection)

            detail_endpoint = detail.get('endpoint')
            if not detail_endpoint:
                detail['endpoint'] = None
                setattr(meta, 'detail', detail)

            collection_endpoint = collection.get('endpoint')
            if not collection_endpoint:
                collection['endpoint'] = None
                setattr(meta, 'collection', collection)


class Resource(object, metaclass=ResourceMetaClass):

    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        obj._fields = copy.deepcopy(obj._fields)
        return obj

    def __init__(self, *args, **kwargs):
        self._partial = False
        self._init(*args, **kwargs)

    @classmethod
    def partial(cls, *args, **kwargs):
        resource = cls.__new__(cls)
        resource._partial = True
        resource.clear()
        resource._init(*args, **kwargs)
        return resource

    # is there a better way to do this?
    @classmethod
    def init_from_obj(cls, obj, partial=False, **kwargs):
        resource = cls.__new__(cls)
        resource._partial = partial
        if resource._partial:
            resource.clear()
        resource.from_obj(obj, **kwargs)
        if not resource._partial:
            resource.validate_full()
        return resource

    @classmethod
    def empty(cls):
        resource = cls.__new__(cls)
        resource._partial = False
        resource.clear()
        return resource

    def _init(self, *args, **kwargs):
        if args and len(args) == 1 and isinstance(args[0], dict):
            self.from_dict(args[0])
        elif args:
            raise Exception('Resource initiation accepts only a dictionary or fields by keyword.')

        if kwargs:
            self.from_dict(kwargs)

        if not self._partial:
            self.validate_full()

    def clear(self):
        for name, field in self._fields.items():
            if self._partial:
                self._set(field, fields.NotSet)
            else:
                if field.flags['default'] == fields.NotSet:
                    self._set(field, None)
                else:
                    field.to_default()

    def from_dict(self, data):
        for name, field in self._fields.items():
            if name in data:
                self._set(field, data[name])
        return self

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
                    self._set(field, val)

        for res_name, obj_name in mapping.items():
            if res_name and obj_name:
                val = getattr(obj, obj_name)
                self._set(self._fields[res_name], val)
        return self

    def to_obj(self, obj, mapping={}, explicit_mapping=False, partial=False):
        """
        Maps the fields from the resource to an object based on identical names. Optional mapping
        parameter allows for discrepancies in naming with resource names being the
        key and the object attribute name to map to being the value. If explicit_mapping is True,
        only the attributes in the mapping dictionary will be copied.
        """
        if not explicit_mapping:
            for name, field in self.valid_fields():
                if hasattr(obj, name):
                    setattr(obj, name, field.get())

        # reconsider this
        for res_name, obj_name in mapping.items():
            raise NotImplementedError()
            if res_name and obj_name:
                val = self._fields[res_name].get()
                if not partial or val != fields.NotSet:
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

    def _set(self, field, value):
        if not self._partial and value == fields.NotSet:
            raise errors.ValidationError('Attempted to set field {0} of a non-partial resource to NotSet'.format(field))
        return field.set(value)