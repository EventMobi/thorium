from . import errors
from .exception_handler import ExceptionHandler
from threading import Lock

_logger_lock = Lock()


class Thorium(object):

    # The logging format used for the debug logger.  This is only used when
    # the application is in debug mode, otherwise the attached logging
    # handler does the formatting.
    debug_log_format = (
        '-' * 80 + '\n' +
        '%(levelname)s in %(module)s [%(pathname)s:%(lineno)d]:\n' +
        '%(message)s\n' +
        '-' * 80
    )

    exception_cls = ExceptionHandler

    def __init__(self, settings, route_manager, debug=False):
        self._logger = None
        self.logger_name = 'thorium'
        self._settings = settings or {}
        self._route_manager = route_manager
        self.debug_on = debug
        self.exception_handler = self.exception_cls(self.logger)
        self._bind_routes()

    @property
    def logger(self):
        """A :class:`logging.Logger` object for this application.
        """
        if self._logger and self._logger.name == self.logger_name:
            return self._logger
        with _logger_lock:
            if self._logger and self._logger.name == self.logger_name:
                return self._logger
            from .logging import create_logger
            self._logger = rv = create_logger(self.logger_name, self.debug_on, self.debug_log_format)
            return rv