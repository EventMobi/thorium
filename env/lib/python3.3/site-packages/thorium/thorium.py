class Thorium(object):

    def __init__(self, settings, route_manager):
        self._settings = settings
        self._route_manager = route_manager
        self._bind_routes()

    def _bind_routes(self):
        raise NotImplementedError()