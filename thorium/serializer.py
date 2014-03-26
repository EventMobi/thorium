import json


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
        return {'type': response_type, 'status': status, 'error': error, 'data': data, 'meta': meta}

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