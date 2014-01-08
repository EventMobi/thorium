import json
from .response import DetailResponse, CollectionResponse


class SerializerBase(object):

    def serialize_response(self, response):
        if isinstance(response, DetailResponse):
            body = {}
            if response.resource:
                response.resource.validate_full()
                body = {n: v.get() for n, v in response.resource.all_fields()}
            serialized_body = self._serialize_data(body)
        elif isinstance(response, CollectionResponse):
            body = {'items': [], '_meta': response.meta}
            if response.resources:
                for res in response.resources:
                    res.validate_full()
                    body['items'].append({n: v.get() for n, v in res.all_fields()})
            serialized_body = self._serialize_data(body)
        else:
            raise Exception('Unexpected response object: {0}'.format(response))
        return serialized_body

    def _serialize_data(self, data):
        raise NotImplementedError('Do not use Serializer directly.')


class JsonSerializer(SerializerBase):

    def _serialize_data(self, data):
        return json.dumps(data, default=handler)


def handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError('Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj)))