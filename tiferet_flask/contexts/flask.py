# *** imports

# ** core
from typing import Dict, Any
import base64

# ** infra
import jwt
from flask import Flask, Blueprint
from tiferet.contexts.app import (
    AppInterfaceContext, 
    RequestContext
)
from tiferet.contexts.request import RequestContext
from tiferet.contexts.error import ErrorContext
from tiferet.contexts.feature import FeatureContext
from tiferet.contexts.logging import LoggingContext
from tiferet.models import ModelObject
from tiferet.commands import parse_parameter

# ** app
from ..handlers.flask import FlaskApiHandler
from ..models.flask import FlaskBlueprint

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

    # * jwt_token_secret
    jwt_token_secret: str

    # * jwt_token_secret_algo
    jwt_token_secret_algo: str

    # * init
    def __init__(self, 
        interface_id: str,
        features: FeatureContext,
        errors: ErrorContext,
        logging: LoggingContext,
        flask_api_handler: FlaskApiHandler,
        jwt_token_secret: str = None,
        jwt_token_secret_algo: str = 'HS256'
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
        :param jwt_token_secret: The JWT token secret.
        :type jwt_token_secret: str
        :param jwt_token_secret_algo: The JWT token secret algorithm.
        :type jwt_token_secret_algo: str
        '''

        # Set the attributes.
        self.flask_api_handler = flask_api_handler

        # Parse the JWT token secret and algorithm if they happen to be environment variables.
        self.jwt_token_secret = parse_parameter.execute(jwt_token_secret)
        self.jwt_token_secret_algo = parse_parameter.execute(jwt_token_secret_algo) 

        # Call the parent constructor.
        super().__init__(interface_id, features, errors, logging)

    # * method: parse_auth_header
    def parse_auth_header(self, auth_header: str, **kwargs) -> Dict[str, str]:
        '''
        Parse the authorization header.

        :param auth_header: The authorization header.
        :type auth_header: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The parsed authorization header.
        :rtype: dict
        '''

        # Return an empty dictionary if the authorization header is not present.
        if not auth_header:
            return {}
        
        # Parse the authorization header.
        token_type, token = auth_header.split(' ')

        # Parse the token based on the token type.
        if token_type.lower() == 'basic':
            return self.parse_basic_auth_header(token)
        elif token_type.lower() == 'bearer':
            return self.parse_jwt_auth_header(token, **kwargs)

    # * method: parse_basic_auth_header
    def parse_basic_auth_header(self, token: str) -> Dict[str, str]:
        '''
        Parse the basic authorization header.

        :param token: The token.
        :type token: str
        :return: The parsed basic authorization header.
        :rtype: dict
        '''

        # Decode the token.
        value = base64.b64decode(token).decode('utf-8')
        client_id, client_secret = value.split(':')

        # Return the client ID and client secret.
        return dict(client_id=client_id, client_secret=client_secret)
    
    # * method: parse_jwt_auth_header
    def parse_jwt_auth_header(self, token: str) -> Dict[str, str]:
        '''
        Parse the JWT authorization header.

        :param token: The token.
        :type token: str
        :return: The parsed JWT authorization header.
        :rtype: dict
        '''
    
        # Decode the token.
        return dict(**jwt.decode(
            token, 
            self.jwt_token_secret, 
            algorithms=[self.jwt_token_secret_algo]
        ))

    def parse_request(self, headers: Dict[str, str] = {}, data: Dict[str, Any] = {}) -> RequestContext:
        '''
        Parse the request context from the Flask request object.

        :param headers: The request headers.
        :type headers: dict
        :param data: The request data.
        :type data: dict
        :return: The request context.
        :rtype: RequestContext
        '''

        # Get the authorization header if applicable and update the headers.
        authorization = self.parse_auth_header(headers.get('Authorization', None))
        headers.update(authorization)

        # Assemble and return the request context.
        return super().parse_request(
            headers=headers,
            data=data
        )
    
    def handle_response(self, request: RequestContext) -> Any:
        '''
        Handle the response from the request context.

        :param request: The request context.
        :type request: RequestContext
        :return: The response.
        :rtype: Any
        '''

        # Handle the response from the request context.
        response, status_code = super().handle_response(request)

        # If the response is None, return an empty response.
        if response is None:
            return ''
        
        # Convert the response to a dictionary if it's a ModelObject.
        if isinstance(response, ModelObject):
            return response.to_primitive()
        
        # If the response is a list containing model objects, convert each to a dictionary.
        if isinstance(response, list) and all(isinstance(item, ModelObject) for item in response):
            return [item.to_primitive() for item in response]
        
        # Return the result as JSON with the specified status code.
        return response, status_code

    # * method: build_blueprint
    def build_blueprint(self, flask_blueprint: FlaskBlueprint, view_func: callable, **kwargs) -> Blueprint:
        '''
        Assembles a Flask blueprint from the given FlaskBlueprint model.

        :param flask_blueprint: The FlaskBlueprint model.
        :type flask_blueprint: FlaskBlueprint
        :param view_func: The view function to handle requests.
        :type view_func: callable
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The created Flask blueprint.
        :rtype: Blueprint
        '''

        # Create the blueprint.
        blueprint = Blueprint(
            flask_blueprint.id, 
            __name__, 
            url_prefix=flask_blueprint.url_prefix
        )

        # Add the url rules.
        [
            blueprint.add_url_rule(
                route.rule, 
                route.id, 
                methods=route.methods, 
                view_func=lambda: view_func(self, **kwargs),
            ) for route in flask_blueprint.routes
        ]
            
        # Return the created blueprint.
        return blueprint
    
    # * method: build_flask_app
    def build_flask_app(self, view_func: callable, **kwargs) -> Flask:
        '''
        Build and return a Flask application instance.

        :param view_func: The view function to handle requests.
        :type view_func: callable
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