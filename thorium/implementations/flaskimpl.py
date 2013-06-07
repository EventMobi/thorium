from .. import Thorium
from ..dispatcher import Dispatcher
from flask import Flask
from flask import request as flaskrequest


class ThoriumFlask(Thorium):

    def __init__(self, settings):
        super(ThoriumFlask, self).__init__(settings)

    def run(self, host=None, debug=False):

        #create flask object
        app = Flask(self.settings['project']['name'])

        #generates a endpoint function for each route and creates a mapping within flask
        for route in self.routes:
            endpoint = self.create_flask_endpoint(route)
            app.add_url_rule(route.path, route.resource.__name__, endpoint)

        # start flask
        app.run(host=host, debug=debug)

    def create_flask_endpoint(self, route):

        #create one flask dispatcher per endpoint, state maintained by the closure
        flask_dispatcher = FlaskDispatcher(route.resource)

        #function to map the endpoint to, calls into the dispatcher
        def _request_handler():
            return flask_dispatcher.dispatch()

        return _request_handler


class FlaskDispatcher(object):
    """
    This class is responsible for pulling data out of a Flask request, building a Thorium request object,
    and injecting it into the Dispatcher
    """

    def __init__(self, resource):
        self.dispatcher = Dispatcher(resource)

    #yo dawg, I heard you like dispatching
    def dispatch(self):
        request = flaskrequest #convert flaskrequest to thorium request here
        return self.dispatcher.dispatch(request)
