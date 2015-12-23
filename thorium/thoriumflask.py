# -*- coding: utf-8 -*-

import traceback

from flask import Response as FlaskResponse, request as flaskrequest
from werkzeug.exceptions import BadRequest as WerkzeugBadRequest

from . import Thorium, errors
from .request import Request
from .resources import VALID_METHODS, VALID_QUERY_PARAMETERS
from .parameters import ParametersMetaClass
from .crossdomain_decorator import crossdomain


class ThoriumFlask(Thorium):

    def __init__(self, settings, route_manager, flask_app):
        self._flask_app = flask_app
        super(ThoriumFlask, self).__init__(
            settings=settings,
            route_manager=route_manager,
            debug=self._flask_app.debug,
        )

    def _bind_routes(self):
        routes = self._route_manager.get_all_routes()
        for r in routes:
            if r.path:
                fep = FlaskEndpoint(
                    dispatcher=r.dispatcher,
                    exception_handler=self.exception_handler,
                    flask_config=self._flask_app.config,
                )
                fep.__name__ = r.name
                self._flask_app.add_url_rule(
                    rule=r.path,
                    endpoint=r.name,
                    view_func=fep.endpoint_target,
                    methods=VALID_METHODS,
                )


class FlaskEndpoint(object):

    def __init__(self, dispatcher, exception_handler, flask_config):
        self.flask_config = flask_config
        self.dispatcher = dispatcher
        # should this just have a reference to the thorium object?
        self.exception_handler = exception_handler

    @crossdomain(origin='*')
    def endpoint_target(self, **kwargs):
        url = method = 'unknown'
        request = None
        try:
            request = self.build_request()
            url = request.url
            method = request.method
            response, serialized_body = self.dispatcher.dispatch(request)
            return FlaskResponse(
                response=serialized_body,
                headers=response.headers,
                status=response.status_code,
                content_type='application/json',
            )
        except errors.HttpErrorBase as e:
            error_body = self.exception_handler.handle_http_exception(
                http_error=e,
                request=request,
            )
            return FlaskResponse(
                response=error_body,
                status=e.status_code,
                headers=e.headers,
                content_type='application/json',
            )
        except Exception as e:
            error_body = self.exception_handler.handle_general_exception(
                url=url,
                method=method,
                e=e,
                request=request,
            )
            # if flask debug raise exception instead of returning json response
            if self.flask_config['DEBUG']:
                raise e
            return FlaskResponse(
                response=error_body,
                status=500,
                headers={},
                content_type='application/json',
            )

    def build_request(self):
        try:
            resource = None
            resources = []
            if flaskrequest.method.lower() in {'post', 'patch', 'put'}:
                if flaskrequest.mimetype == 'application/json':
                    json_data = flaskrequest.json or {}
                    partial = True if flaskrequest.method == 'PATCH' else False

                    # hack for single or list resources
                    if isinstance(json_data, list):
                        for i in json_data:
                            resources.append(self._create_resource(i, partial))
                    else:
                        resource = self._create_resource(json_data, partial)

                else:
                    raise errors.BadRequestError(
                        'Currently only json is supported, use application/'
                        'json mimetype')

            return Request(
                dispatcher=self.dispatcher,
                method=flaskrequest.method,
                identifiers=flaskrequest.view_args,
                query_params=self._build_parameters(),
                mimetype=flaskrequest.mimetype,
                resource=resource,
                resources=resources,
                url=flaskrequest.url,
            )
        except (errors.ValidationError, WerkzeugBadRequest) as e:
            raise errors.BadRequestError(message=e.args[0] if e.args else None)

    def _create_resource(self, data, partial):
        # override body data with url identifiers
        data.update(flaskrequest.view_args)
        return data

    def _build_parameters(self):
        if not self.dispatcher.Parameters:
            return None

        flask_params = flaskrequest.args.to_dict() if flaskrequest.args else {}

        if isinstance(self.dispatcher.Parameters, ParametersMetaClass):
            return self.dispatcher.Parameters.validate(flask_params)
        else:
            self._validate_no_extra_query_params(flask_params)
            flask_params.update(flaskrequest.view_args)
            params = self.dispatcher.Parameters.init_from_dict(
                data=flask_params,
                partial=True,
                cast=True,
            )
            params.sort = flask_params.get('sort')
            if not hasattr(params, 'offset'):
                params.offset = flask_params.get('offset')
            if not hasattr(params, 'limit'):
                params.limit = flask_params.get('limit')
            return params

    def _validate_no_extra_query_params(self, flask_params):
        param_fields = dict(self.dispatcher.Parameters.all_fields())
        for name, param in flask_params.items():
            if name not in param_fields and name not in VALID_QUERY_PARAMETERS:
                raise errors.ValidationError(
                    '{0} is not a supported query parameter.'.format(name)
                )
