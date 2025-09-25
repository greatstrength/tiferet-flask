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
from tiferet.contexts.request import RequestContext
from tiferet.contexts.error import ErrorContext
from tiferet.contexts.feature import FeatureContext
from tiferet.contexts.logging import LoggingContext

# ** app
from .request import FlaskRequestContext
from ..handlers.flask import FlaskApiHandler
from ..models import FlaskBlueprint

# *** contexts

# ** context: flask_api_context
class FlaskApiContext(AppInterfaceContext):
    '''
    A context for managing Flask API interactions within the Tiferet framework.
    '''

    # * attribute: flask_app
    flask_app: Flask

    # * attribute: flask_api_handler
    flask_api_handler: FlaskApiHandler

    # * init
    def __init__(self, 
        interface_id: str,
        features: FeatureContext,
        errors: ErrorContext,
        logging: LoggingContext,
        flask_api_handler: FlaskApiHandler
    ):
        '''
        Initialize the application interface context.

        :param interface_id: The interface ID.
        :type interface_id: str
        :param features: The feature context.
        :type features: FeatureContext
        :param errors: The error context.
        :type errors: ErrorContext
        :param logging: The logging context.
        :type logging: LoggingContext
        :param flask_api_handler: The Flask API handler.
        :type flask_api_handler: FlaskApiHandler
        '''

        # Call the parent constructor.
        super().__init__(interface_id, features, errors, logging)

        # Set the attributes.
        self.flask_api_handler = flask_api_handler

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
        Handle the error and return the response.

        :param error: The error to handle.
        :type error: Exception
        :return: The error response.
        :rtype: Any
        '''

        # Handle the error and get the response from the parent context.
        if not isinstance(error, TiferetError):
            return super().handle_error(error), 500

        # Get the status code by the error code on the exception.
        status_code = self.flask_api_handler.get_status_code(error.error_code)
        return super().handle_error(error), status_code

    # * method: handle_response
    def handle_response(self, request: RequestContext) -> Any:
        '''
        Handle the response from the request context.

        :param request: The request context.
        :type request: RequestContext
        :return: The response.
        :rtype: Any
        '''

        # Handle the response from the request context.
        response = super().handle_response(request)

        # Retrieve the route by the request feature id.
        route = self.flask_api_handler.get_route(request.feature_id)

        # Return the result as JSON with the specified status code.
        return response, route.status_code

    # * method: build_blueprint
    def build_blueprint(self, flask_blueprint: FlaskBlueprint, view_func: Callable, **kwargs) -> Blueprint:
        '''
        Assembles a Flask blueprint from the given FlaskBlueprint model.

        :param flask_blueprint: The FlaskBlueprint model.
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
                view_func=lambda: view_func(self, **kwargs),
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

        # Load the Flask blueprints.
        blueprints = self.flask_api_handler.get_blueprints()

        # Create and register the blueprints.
        for bp in blueprints:
            blueprint = self.build_blueprint(bp, view_func=view_func, **kwargs)
            flask_app.register_blueprint(blueprint)

        # Set the flask_app attribute.
        self.flask_app = flask_app