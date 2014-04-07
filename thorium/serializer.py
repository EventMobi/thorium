import json
from collections import OrderedDict


class SerializerBase(object):

    def serialize_response(self, response):
        body = self._build_envelope(response_type=response.response_type,
                                    status=response.status_code,
                                    error=response.error,
                                    data=response.get_response_data(),
                                    meta=response.meta)
        serialized_body = self._serialize_data(body)
        return serialized_body

    @staticmethod
    def _build_envelope(response_type, status, error, data, meta):
        envelope = OrderedDict()
        envelope['type'] = response_type
        envelope['status'] = status
        envelope['error'] = error
        envelope['data'] = data
        envelope['meta'] = meta
        return envelope

    def _serialize_data(self, data):
        raise NotImplementedError('This method must be implemented by a subclass.')


class JsonSerializer(SerializerBase):

    def _serialize_data(self, data):
        return json.dumps(data, default=handler)


def handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError('Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj)))