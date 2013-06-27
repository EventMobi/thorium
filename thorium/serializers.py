import json


#move this to it's own file, make it good not bad
class Serializer(object):

    def deserialize(self, request):

        if request.mimetype != 'application/json':
            raise NotImplementedError('Currently only json is supported, use application/json mimetype')

        resource = request.resource()
        resource.from_dict(request.body, convert=True)

        return resource


class DetailSerializer(Serializer):

    def serialize(self, resource):
        return json.dumps(resource.to_dict(), default=handler)


class CollectionSerializer(Serializer):

    def serialize(self, resource_collection):
        data = [resource.to_dict() for resource in resource_collection]
        return json.dumps(data, default=handler)


def handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    #elif isinstance(obj, ...):
    #    return ...
    else:
        raise TypeError('Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj)))