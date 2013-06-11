from ... import Thorium
from ...request import Request
from flask import request as flaskrequest


class ThoriumFlask(Thorium):

    def register_routes(self, flask_app):

        for route in self.routes:
            fep = FlaskEndpoint(route.dispatcher)
            flask_app.add_url_rule(route.path, route.name, fep.endpoint)


class FlaskEndpoint(object):

    def __init__(self, dispatcher):
        self.dispatcher = dispatcher

    def endpoint(self):
        request = Request(flaskrequest.method)
        return self.dispatcher.dispatch(request)
