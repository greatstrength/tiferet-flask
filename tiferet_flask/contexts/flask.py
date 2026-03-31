# *** imports

# ** core
from typing import Any, Callable

# ** infra
from flask import Flask, Blueprint
from tiferet.contexts.app import (
    AppInterfaceContext,
    RequestContext,
    TiferetError
)
from tiferet import TiferetAPIError
from tiferet.contexts.error import ErrorContext
from tiferet.contexts.feature import FeatureContext
from tiferet.contexts.logging import LoggingContext

# ** app
from .request import FlaskRequestContext
from ..domain import FlaskBlueprint

# *** contexts

# ** context: flask_api_context
class FlaskApiContext(AppInterfaceContext):
    '''
    A context for managing Flask API interactions within the Tiferet framework.
    '''

    # * attribute: flask_app
    flask_app: Flask

    # * attribute: get_blueprints_handler
    get_blueprints_handler: Callable

    # * attribute: get_route_handler
    get_route_handler: Callable

    # * attribute: get_status_code_handler
    get_status_code_handler: Callable

    # * init
    def __init__(self,
        interface_id: str,
        features: FeatureContext,
        errors: ErrorContext,
        logging: LoggingContext,
        get_blueprints_handler: Callable,
        get_route_handler: Callable,
        get_status_code_handler: Callable
    ):
        '''
        Initialize the Flask API context.

        :param interface_id: The interface ID.
        :type interface_id: str
        :param features: The feature context.
        :type features: FeatureContext
        :param errors: The error context.
        :type errors: ErrorContext
        :param logging: The logging context.
        :type logging: LoggingContext
        :param get_blueprints_handler: Callable to retrieve all Flask blueprints.
        :type get_blueprints_handler: Callable
        :param get_route_handler: Callable to retrieve a Flask route by endpoint.
        :type get_route_handler: Callable
        :param get_status_code_handler: Callable to retrieve HTTP status code for an error code.
        :type get_status_code_handler: Callable
        '''

        # Call the parent constructor.
        super().__init__(interface_id, features, errors, logging)

        # Set the handler callables.
        self.get_blueprints_handler = get_blueprints_handler
        self.get_route_handler = get_route_handler
        self.get_status_code_handler = get_status_code_handler

    # * method: parse_request
    def parse_request(self, headers: dict = {}, data: dict = {}, feature_id: str = None, **kwargs) -> FlaskRequestContext:
        '''
        Parse the incoming request and return a FlaskRequestContext instance.

        :param headers: The request headers.
        :type headers: dict
        :param data: The request data.
        :type data: dict
        :param feature_id: The feature ID.
        :type feature_id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A FlaskRequestContext instance.
        :rtype: FlaskRequestContext
        '''

        # Return a FlaskRequestContext instance.
        return FlaskRequestContext(
            headers=headers,
            data=data,
            feature_id=feature_id,
        )

    # * method: handle_error
    def handle_error(self, error: Exception) -> Any:
        '''
        Handle the error and return the response with status code.

        :param error: The error to handle.
        :type error: Exception
        :return: The error response tuple (response, status_code).
        :rtype: Any
        '''

        # Determine the status code before formatting.
        if not isinstance(error, TiferetError):
            status_code = 500
        else:
            status_code = self.get_status_code_handler(error_code=error.error_code)

        # Format the error via the parent, catching the TiferetAPIError it raises.
        try:
            super().handle_error(error)
        except TiferetAPIError as api_error:
            return dict(
                error_code=api_error.error_code,
                name=api_error.name,
                message=api_error.message,
            ), status_code

    # * method: handle_response
    def handle_response(self, request: RequestContext) -> Any:
        '''
        Handle the response from the request context.

        :param request: The request context.
        :type request: RequestContext
        :return: The response tuple (response, status_code).
        :rtype: Any
        '''

        # Handle the response from the request context.
        response = super().handle_response(request)

        # Retrieve the route by the request feature id via the handler callable.
        route = self.get_route_handler(endpoint=request.feature_id)

        # Return the result as JSON with the specified status code.
        return response, route.status_code

    # * method: build_blueprint
    def build_blueprint(self, flask_blueprint: FlaskBlueprint, view_func: Callable, **kwargs) -> Blueprint:
        '''
        Assembles a Flask blueprint from the given FlaskBlueprint domain object.

        :param flask_blueprint: The FlaskBlueprint domain object.
        :type flask_blueprint: FlaskBlueprint
        :param view_func: The view function to handle requests.
        :type view_func: Callable
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The created Flask blueprint.
        :rtype: Blueprint
        '''

        # Create the blueprint.
        blueprint = Blueprint(
            flask_blueprint.name,
            __name__,
            url_prefix=flask_blueprint.url_prefix
        )

        # Add the url rules.
        for route in flask_blueprint.routes:
            blueprint.add_url_rule(
                route.rule,
                route.id,
                methods=route.methods,
                view_func=view_func,
            )

        # Return the created blueprint.
        return blueprint

    # * method: build_flask_app
    def build_flask_app(self, view_func: Callable, **kwargs) -> Flask:
        '''
        Build and return a Flask application instance.

        :param view_func: The view function to handle requests.
        :type view_func: Callable
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A Flask application instance.
        :rtype: Flask
        '''

        # Import CORS here to avoid circular import issues.
        from flask_cors import CORS

        # Create the Flask application.
        # Enable CORS for the Flask application.
        flask_app = Flask(__name__)
        CORS(flask_app)

        # Load the Flask blueprints via the handler callable.
        blueprints = self.get_blueprints_handler()

        # Create and register the blueprints.
        for bp in blueprints:
            blueprint = self.build_blueprint(bp, view_func=view_func, **kwargs)
            flask_app.register_blueprint(blueprint)

        # Set the flask_app attribute.
        self.flask_app = flask_app
