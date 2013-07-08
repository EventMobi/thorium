import json
from . import Thorium
from .request import Request
from .errors import HttpErrorBase
from .resources import VALID_METHODS
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
        status = 200
        headers = {}
        content_type = 'application/json'

        try:
            request = Request(method=flaskrequest.method, identifiers=flaskrequest.view_args,
                              resource=self.dispatcher.resource, query_params=flaskrequest.args.to_dict(),
                              mimetype=flaskrequest.mimetype, body=flaskrequest.json)
            response = self.dispatcher.dispatch(request)
        except HttpErrorBase as e:
            response = json.dumps({'error': str(e), 'status': e.status_code})
            status = e.status_code
            headers.update(e.headers)
        return Response(response=response, status=status, headers=headers, content_type=content_type)

