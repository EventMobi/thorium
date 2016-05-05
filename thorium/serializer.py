# -*- coding: utf-8 -*-

import json
import uuid

from collections import OrderedDict

from .datastructures import NotSet


class SerializerBase(object):

    def serialize_response(self, response):
        meta = response.meta
        if meta['pagination'] is not None:
            if meta['pagination']['limit'] is NotSet:
                meta['pagination']['limit'] = None
            if meta['pagination']['offset'] is NotSet:
                meta['pagination']['offset'] = None
        body = self._build_envelope(response_type=response.response_type,
                                    status=response.status_code,
                                    error=response.error,
                                    code=getattr(response, 'code', None),
                                    params=getattr(response, 'params', None),
                                    data=response.get_response_data(),
                                    meta=meta)
        serialized_body = self._serialize_data(body)
        return serialized_body

    @staticmethod
    def _build_envelope(response_type, status, error, code, params, data, meta):
        envelope = OrderedDict()
        envelope['type'] = response_type
        envelope['status'] = status
        envelope['error'] = error
        envelope['error_code'] = code
        envelope['errors'] = [
            {
                'level': 'error',   # Only pass back errors for now
                'code': code,
                'params': params,
            }
        ] if code else None
        envelope['data'] = data
        envelope['meta'] = meta
        return envelope

    def _serialize_data(self, data):
        err_msg = 'This method must be implemented by a subclass.'
        raise NotImplementedError(err_msg)


class JsonSerializer(SerializerBase):

    def _serialize_data(self, data):
        return json.dumps(data, default=handler)


def handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    elif isinstance(obj, uuid.UUID):
        return str(obj)
    elif isinstance(obj, bytes):
        return obj.decode('utf-8')
    else:
        err_msg = 'Object of type %s with value of %s is not JSON serializable'
        raise TypeError(err_msg % (type(obj), repr(obj)))
