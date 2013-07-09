import json
from . import Thorium
from .request import Request
from .errors import HttpErrorBase
from .resources import VALID_METHODS
from .response import DetailResponse, CollectionResponse
from flask import Response, request as flaskrequest


class ThoriumFlask(Thorium):

    def __init__(self, settings, route_manager, flask_app):
        self._flask_app = flask_app
        super(ThoriumFlask, self).__init__(settings=settings, route_manager=route_manager)

    def _bind_routes(self):
        routes = self._route_manager.get_all_routes()
        for r in routes:
            fep = FlaskEndpoint(r.dispatcher)
            self._flask_app.add_url_rule(r.path, r.name, fep.endpoint_target, methods=VALID_METHODS)


class FlaskEndpoint(object):

    def __init__(self, dispatcher):
        self.dispatcher = dispatcher

    def endpoint_target(self, **kwargs):
        try:
            request = self.build_request()
            response = self.dispatcher.dispatch(request)
            return self.convert_response(response)
        except HttpErrorBase as e:
            error = json.dumps({'error': str(e), 'status': e.status_code})
            return Response(response=error, status=e.status_code, headers=e.headers, content_type='application/json')

    def build_request(self):
        resource = None

        if flaskrequest.data:
            if flaskrequest.mimetype == 'application/json':
                if flaskrequest.json:
                    resource = self.dispatcher.resource_cls()
                    resource.from_dict(flaskrequest.json, convert=True)
            else:
                raise NotImplementedError('Currently only json is supported, use application/json mimetype')

        request = Request(method=flaskrequest.method, identifiers=flaskrequest.view_args,
                          resource_cls=self.dispatcher.resource_cls, query_params=flaskrequest.args.to_dict(),
                          mimetype=flaskrequest.mimetype, resource=resource, request_type=self.dispatcher.request_type,
                          url=flaskrequest.url)

        return request

    def convert_response(self, response):
        body = None
        if isinstance(response, DetailResponse):
            if response.resource:
                body = json.dumps(response.resource.to_dict(), default=handler)
        elif isinstance(response, CollectionResponse):
            if response.resources:
                data = [resource.to_dict() for resource in response.resources]
                body = json.dumps(data, default=handler)
        else:
            raise Exception('Unexpected response object: {0}'.format(response))

        return Response(response=body, status=200, headers=response.headers, content_type='application/json')


def handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    #elif isinstance(obj, ...):
    #    return ...
    else:
        raise TypeError('Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj)))