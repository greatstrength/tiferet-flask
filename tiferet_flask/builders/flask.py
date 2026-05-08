"""Flask API Builder."""

# *** imports

# ** core
from typing import Callable, List

# ** infra
from flask import Flask, Blueprint
from flask_cors import CORS
from tiferet.builders import AppBuilder

# ** app
from ..domain import FlaskBlueprint
from ..contexts import FlaskApiContext

# *** builders

# ** builder: flask_app_builder
class FlaskAppBuilder(AppBuilder):
    '''
    Specialized application builder for Flask applications.
    '''

    # * method: get_blueprints
    def get_blueprints(self) -> List[FlaskBlueprint]:
        '''
        Resolve and execute the get_blueprints event from the service provider.

        :return: A list of FlaskBlueprint domain objects.
        :rtype: List[FlaskBlueprint]
        '''

        # Resolve the get_blueprints event and execute it.
        get_blueprints_evt = self.service_provider.get_service('get_blueprints_evt')
        return get_blueprints_evt.execute()

    # * method: build_blueprint
    def build_blueprint(self, flask_blueprint: FlaskBlueprint, view_func: Callable, **kwargs) -> Blueprint:
        '''
        Build a Flask Blueprint from a FlaskBlueprint domain object.

        :param flask_blueprint: The FlaskBlueprint domain object.
        :type flask_blueprint: FlaskBlueprint
        :param view_func: The view function to handle requests.
        :type view_func: Callable
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A configured Flask Blueprint instance.
        :rtype: Blueprint
        '''

        # Create the Flask Blueprint.
        blueprint = Blueprint(
            flask_blueprint.name,
            __name__,
            url_prefix=flask_blueprint.url_prefix,
        )

        # Add routes from the FlaskBlueprint domain object.
        for route in flask_blueprint.routes:
            blueprint.add_url_rule(
                route.rule,
                route.id,
                methods=route.methods,
                view_func=view_func,
            )

        # Return the configured blueprint.
        return blueprint

    # * method: build_flask_app
    def build_flask_app(self, interface_id: str, view_func: Callable, **kwargs) -> Flask:
        '''
        Build a complete Flask application with CORS and blueprints.

        :param interface_id: The interface ID to load.
        :type interface_id: str
        :param view_func: The view function to handle requests.
        :type view_func: Callable
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A configured Flask application instance.
        :rtype: Flask
        '''

        # Load the interface context.
        interface_context = self.load_interface(interface_id)

        # Create the Flask application with CORS.
        flask_app = Flask(__name__)
        CORS(flask_app)

        # Load and register blueprints.
        blueprints = self.get_blueprints()
        for bp in blueprints:
            blueprint = self.build_blueprint(bp, view_func=view_func, **kwargs)
            flask_app.register_blueprint(blueprint)

        # Return the assembled Flask application.
        return flask_app

    # * method: run
    def run(self, interface_id: str, view_func: Callable, **kwargs) -> Flask:
        '''
        Build and return a ready-to-serve Flask application.

        :param interface_id: The interface ID to load.
        :type interface_id: str
        :param view_func: The view function to handle requests.
        :type view_func: Callable
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A configured Flask application instance.
        :rtype: Flask
        '''

        # Build and return the Flask application.
        return self.build_flask_app(interface_id, view_func, **kwargs)
