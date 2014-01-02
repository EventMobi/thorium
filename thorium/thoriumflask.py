import json
import traceback
from . import Thorium, errors
from .request import Request
from .resources import VALID_METHODS
from .response import DetailResponse, CollectionResponse
from flask import Response as FlaskResponse, request as flaskrequest
from .crossdomain_decorator import crossdomain


class ThoriumFlask(Thorium):

    def __init__(self, settings, route_manager, flask_app):
        self._flask_app = flask_app
        super(ThoriumFlask, self).__init__(settings=settings, route_manager=route_manager, debug=self._flask_app.debug)

    def _bind_routes(self):
        routes = self._route_manager.get_all_routes()
        for r in routes:
            if r.path:
                fep = FlaskEndpoint(r.dispatcher, self.exception_handler, self._flask_app.config)
                self._flask_app.add_url_rule(r.path, r.name, fep.endpoint_target, methods=VALID_METHODS)


class FlaskEndpoint(object):

    def __init__(self, dispatcher, exception_handler, flask_config):
        self.flask_config = flask_config
        self.dispatcher = dispatcher
        self.exception_handler = exception_handler  # should this just have a reference to the thorium object?

    @crossdomain(origin='*')
    def endpoint_target(self, **kwargs):
        try:
            request = self.build_request()
            response = self.dispatcher.dispatch(request)
            return self.convert_response(response)
        except errors.HttpErrorBase as e:
            error_body = self.exception_handler.handle_http_exception(e)
            return FlaskResponse(response=error_body, status=e.status_code, headers=e.headers, content_type='application/json')
        except Exception as e:
            route = 'test_route'
            method = 'test_method'
            error_body = self.exception_handler.handle_general_exception(route, method, e)
            if self.flask_config['DEBUG']:  # if flask debug raise exception instead of returning json response
                raise e
            return FlaskResponse(response=error_body, status=500, headers={}, content_type='application/json')

    def _create_resource(self, data, partial):
        if partial:
            resource = self.dispatcher.resource_cls.partial()
        else:
            resource = self.dispatcher.resource_cls()
        resource.from_dict(data)
        if not partial:
            resource.validate_full()
        return resource

    def build_request(self):
        try:
            resource = None
            resources = []
            if flaskrequest.data:
                if flaskrequest.mimetype == 'application/json':
                    if flaskrequest.json:
                        partial = True if flaskrequest.method == 'PATCH' else False

                        #hack for single or list resources
                        if isinstance(flaskrequest.json, list):
                            for i in flaskrequest.json:
                                resources.append(self._create_resource(i, partial))
                        else:
                            resource = self._create_resource(flaskrequest.json, partial)

                else:
                    raise errors.BadRequestError('Currently only json is supported, use application/json mimetype')

            return Request(method=flaskrequest.method, identifiers=flaskrequest.view_args,
                           resource_cls=self.dispatcher.resource_cls, query_params=flaskrequest.args.to_dict(),
                           mimetype=flaskrequest.mimetype, resource=resource, resources=resources,
                           request_type=self.dispatcher.request_type, url=flaskrequest.url)
        except errors.ValidationError as e:
            raise errors.BadRequestError(message=e.args[0])

    def convert_response(self, response):
        body = None
        if isinstance(response, DetailResponse):
            if response.resource:
                response.resource.validate_full()
                data = {n: v.get() for n, v in response.resource.all_fields()}
                body = json.dumps(data, default=handler)
        elif isinstance(response, CollectionResponse):
            if response.resources:
                data = []
                for res in response.resources:
                    res.validate_full()
                    data.append({n: v.get() for n, v in res.all_fields()})
                body = json.dumps(data, default=handler)
        else:
            raise Exception('Unexpected response object: {0}'.format(response))

        return FlaskResponse(response=body, headers=response.headers, status=response.status_code, content_type='application/json')


def handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError('Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj)))