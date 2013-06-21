from fields import ResourceField
import copy


#Note: will likely need some sort of sorted dictionary to maintain field order
def _get_fields(bases, attrs):
    fields = {name: attrs.pop(name) for name, field in list(attrs.iteritems()) if isinstance(field, ResourceField)}

    # If this class is subclassing another ResourceInterface, add that Resource's
    # fields.  Note that we loop over the bases in *reverse*. This is necessary
    # in order to maintain the correct order of fields.
    # Borrowed from Django Rest Framework.
    for base in bases[::-1]:
        if hasattr(base, 'fields'):
            fields = dict(base.fields.items() + fields.items())

    return fields


class ResourceInterfaceMetaClass(type):
    def __new__(mcs, name, bases, attrs):
        attrs['fields'] = _get_fields(bases, attrs)
        return super(ResourceInterfaceMetaClass, mcs).__new__(mcs, name, bases, attrs)


class ResourceInterfaceBase(object):
    """ Base class for all Resources. Responsible for common behaviour such as managing
    fields.
    """
    def __init__(self):
        self.fields = copy.deepcopy(self.fields)

    # def __setattr__(self, name, value):
    #     field = getattr(self, name)
    #     if isinstance(field, ResourceField):
    #         field.set(value)
    #     else:
    #         raise Exception('Can only assign to Fields')


class ResourceInterface(ResourceInterfaceBase):
    #Note this won't work in python 3, syntax changed to: class Abc(metaclass=meta):
    __metaclass__ = ResourceInterfaceMetaClass


class CollectionResourceInterface(ResourceInterface):
    """ Base class for collections of Resources. """
    pass


class DetailResourceInterface(ResourceInterface):
    """ Base class for the details of a ResourceInterface. """
    pass


class Resource(object):
    """ A collection of :class:`.ResourceField`'s """

    def __init__(self, fields):
        self.fields = fields


class ResourceManager(object):
    """ Manages :class:`.Resource` objects. """

    def __init__(self, resource_cls):
        self.resource_cls = resource_cls

    def detail_from_native(self, data):
        """ Returns a dictionary of fields with values mapped from data. """
        return self._create_resource(self._map_fields(data))

    def collection_from_native(self, data_collection):
        """ Returns a list of dictionaries of fields with values mapped from data_collection  """
        return [self._create_resource(self._map_fields(data)) for data in data_collection]

    def _create_resource(self, fields):
        """ Creates a :class:`.Resource` from a dictionary of :class:`.ResourceField`'s """
        return Resource(fields)

    def _map_fields(self, data):
        """ Returns a dictionary of fields with values mapped from data. """
        fields = self._get_fields()
        for key, field in fields.items():
            field.set(data[key]) #note catch KeyError here and raise expected fields not found error
        return fields

    def _get_fields(self):
        """ Creates a new dictionary of fields from the resource. """
        return copy.deepcopy(self.resource_cls.fields)