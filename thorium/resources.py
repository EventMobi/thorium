from . import errors, fields, NotSet
import copy
import collections

VALID_METHODS = {'get', 'post', 'put', 'patch', 'delete', 'options'}


class ResourceMetaClass(type):

    #Note: attrs comes in alphabetical order, unsure how to maintain declared order of fields
    def __new__(mcs, resource_name, bases, attrs):
        attrs['_fields'] = mcs._get_fields(bases, attrs)
        return super().__new__(mcs, resource_name, bases, attrs)

    #Note: will likely need some sort of sorted dictionary to maintain field order
    @staticmethod
    def _get_fields(bases, attrs):

        # gather fields to add to _fields dictionary
        # also replaces field definition with a property to wrap the _fields dictionary
        field_dict = {}
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
            return self._get(name)
        return get_field_property

    @staticmethod
    def _get_set_prop(name):
        def set_field_property(self, value):
            return self._set(name, value)
        return set_field_property


class Resource(object, metaclass=ResourceMetaClass):
    _fields = {}

    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        obj._values = {name: field.default for name, field in obj.all_fields()}
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
    def init_from_obj(cls, obj, partial=False, mapping=None, explicit_mapping=False, override=None, cast=False):
        mapping = mapping if mapping else {}
        resource = cls.__new__(cls)
        resource._partial = partial
        if resource._partial:
            resource.clear()
        resource.from_obj(obj, mapping, explicit_mapping, override, cast)
        resource.validate()
        return resource

    @classmethod
    def init_from_dict(cls, data, partial=False, cast=False):
        resource = cls.__new__(cls)
        resource._partial = partial
        if resource._partial:
            resource.clear()
        resource.from_dict(data, cast)
        resource.validate()
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
        self.validate()

    def clear(self):
        for name, field in self.all_fields():

            # do nothing with required fields
            if field.is_required:
                continue

            if self._partial:
                self._set(name, NotSet)
            else:
                if field.flags['default'] == NotSet:
                    self._set(name, None)
                else:
                    self.to_default(name)

    def from_dict(self, data, cast=False):
        for name, field in self.all_fields():
            if name in data:
                self._set(name, data[name], cast)
        return self

    def to_dict(self):
        return dict(self.valid_items())

    def from_obj(self, obj, mapping=None, explicit_mapping=False, override=None, cast=False):
        """
        Maps the public attributes from a object to the resource fields based on identical names.
        Optional mapping parameter allows for discrepancies in naming with resource names being the
        key and the object attribute name to map to being the value. If explicit_mapping is True,
        only the attributes in the mapping dictionary will be copied. An optional override dictionary
        is used to set values explicitly.
        """
        if not override:
            override = {}
        for name, field in self.all_fields():

            # If explicate_mapping only names within the mapping will be considered
            if explicit_mapping and name not in mapping:
                continue

            # Convert name to mapped name if available, else use Resource's existing name
            # If there's an override, don't use its mapping
            if mapping and not name in override:
                name = mapping.get(name, name)

            # A None value for name indicates that we shouldn't map this field
            if not name:
                continue

            # Check override for the value first
            value = NotSet
            if override:
                value = override.get(name, NotSet)

            # If we don't have a value from override, attempt to get it from source obj
            if value is NotSet:
                value = getattr(obj, name, NotSet)

            # If we still don't have a value, then continue
            if value is NotSet:
                continue

            self._set(field.name, value, cast)

        return self

    def to_obj(self, obj, mapping=None, explicit_mapping=False, override=None):
        """
        Maps the fields from the resource to an object based on identical names. Optional mapping
        parameter allows for discrepancies in naming with resource names being the
        key and the object attribute name to map to being the value. If explicit_mapping is True,
        only the attributes in the mapping dictionary will be copied.
        """
        if not override:
            override = {}
        for name, field in self.valid_fields():

            # If explicate_mapping only names within the mapping will be considered
            if explicit_mapping and name not in mapping:
                continue

            # Convert name to mapped name if available, else use Resource's existing name
            # If there's an override, don't use its mapping
            if mapping and not name in override:
                name = mapping.get(name, name)

            # A None value for name indicates that we shouldn't map this field
            if not name:
                continue

            # Ensure that target obj has an attribute with a matching name
            if not hasattr(obj, name):
                continue

            # Check override for the value first
            value = override.get(name, NotSet)

            if value is NotSet:
                value = self._get(field.name)

            # Set target obj value from Resource value
            setattr(obj, name, value)

        return obj

    @classmethod
    def all_fields(cls):
        return cls._fields.items()

    def valid_fields(self):
        return ((name, field) for name, field in self.all_fields() if self.is_set(name))

    def sorted_items(self):
        return ((n, self._get(n)) for n, v in sorted(self.all_fields(), key=lambda x: x[1].order_value))

    def items(self):
        return self._values.items()

    def valid_items(self):
        return ((name, field) for name, field in self.items() if self.is_set(name))

    def validate(self):
        if self._partial:
            self._validate_partial()
        else:
            self._validate_full()

    def _validate_full(self):
        for name, field in self._fields.items():
            if not self.is_set(name) and not field.is_readonly:
                raise errors.ValidationError('Field {0} is NotSet, expected full resource.'.format(field))

    def _validate_partial(self):
        for name, field in self._fields.items():
            if not self.is_set(name) and field.is_required:
                raise errors.ValidationError('Field {0} is required, cannot be NotSet even on a partial resource.'
                                             .format(field))

    def to_default(self, field_name):
        self._set(field_name, self._fields[field_name].default)

    @property
    def is_partial(self):
        return self._partial

    def is_set(self, field_name):
        return self._get(field_name) != NotSet

    def _set(self, field_name, value, cast=False):
        field = self._fields[field_name]
        if not self._partial and not field.is_readonly and value == NotSet:
            raise errors.ValidationError('Attempted to set field {0} of a non-partial resource to NotSet'.format(field))
        self._values[field_name] = field.validate(value, cast=cast)
        return self._values[field_name]

    def _get(self, field_name):
        return self._values[field_name]