from . import errors


class Thorium(object):

    def __init__(self, settings, route_manager):
        self._settings = settings or {}
        self._route_manager = route_manager
        self.exception_handler = self._settings.get('exception_handler', errors.ExceptionHandler)
        self._bind_routes()

    def _bind_routes(self):
        raise NotImplementedError()