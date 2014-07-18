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
            return self._values[name]
        return get_field_property

    @staticmethod
    def _get_set_prop(name):
        def set_field_property(self, value):
            return self._set(self._fields[name], value)
        return set_field_property


class Resource(object, metaclass=ResourceMetaClass):

    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        obj._values = collections.OrderedDict(((name, field.flags['default']) for name, field in obj._fields.items()))
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
    def init_from_obj(cls, obj, partial=False, mapping=None, explicit_mapping=False, override=None):
        mapping = mapping if mapping else {}
        resource = cls.__new__(cls)
        resource._partial = partial
        if resource._partial:
            resource.clear()
        resource.from_obj(obj, mapping, explicit_mapping, override)
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
                self._set(field, NotSet)
            else:
                if field.flags['default'] == NotSet:
                    self._set(field, None)
                else:
                    self.field_to_default(field)

    def from_dict(self, data):
        for name, field in self._fields.items():
            if name in data:
                self._set(field, data[name])
        return self

    def to_dict(self):
        return {name: self._values[field.name] for name, field in self.valid_fields()}

    def from_obj(self, obj, mapping=None, explicit_mapping=False, override=None):
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

            self._set(field, value)

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
                value = self._values[field.name]

            # Set target obj value from Resource value
            setattr(obj, name, value)

        return obj

    def valid_fields(self):
        return ((name, field) for name, field in self._fields.items() if self._values[field.name] != NotSet)

    def all_fields(self):
        return ((name, field) for name, field in self._fields.items())

    def all_values(self):
        return ((name, value) for name, value in self._values.items())

    def validate_full(self):
        for field in self._fields.values():
            if self._values[field.name] == NotSet and not field.is_readonly:
                raise errors.ValidationError('Field {0} is NotSet, expected full resource.'.format(field))

    def field_to_default(self, field):
        self._values[field.name] = field.flags['default']

    @property
    def is_partial(self):
        return self._partial

    def _set(self, field, value):
        if not self._partial and not field.is_readonly and value == NotSet:
            raise errors.ValidationError('Attempted to set field {0} of a non-partial resource to NotSet'.format(field))
        self._values[field.name] = field.set(value)
        return self._values[field.name]