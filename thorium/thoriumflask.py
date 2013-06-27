from . import Thorium
from .request import Request
from flask import request as flaskrequest


class ThoriumFlask(Thorium):

    def __init__(self, settings, route_manager, flask_app):
        self._flask_app = flask_app
        super(ThoriumFlask, self).__init__(settings=settings, route_manager=route_manager)

    def _bind_routes(self):
        routes = self._route_manager.get_all_routes()
        for r in routes:
            fep = FlaskEndpoint(r.dispatcher)
            self._flask_app.add_url_rule(r.endpoint, r.name, fep.endpoint, methods=r.dispatcher.allowed_methods)


class FlaskEndpoint(object):

    def __init__(self, dispatcher):
        self.dispatcher = dispatcher

    def endpoint(self, **kwargs):
        request = Request(method=flaskrequest.method, identifiers=flaskrequest.view_args,
                          resource=self.dispatcher.resource, query_params=flaskrequest.args.to_dict(),
                          mimetype=flaskrequest.mimetype, body=flaskrequest.json)
        return self.dispatcher.dispatch(request)

