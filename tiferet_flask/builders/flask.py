'''Flask API Builder.'''

# *** imports

# ** core
from typing import Callable, List

# ** infra
from flask import Flask, Blueprint
from flask_cors import CORS
from tiferet.builders import AppBuilder
from tiferet_openapi import ApiRouter


# *** builders

# ** builder: flask_app_builder
class FlaskAppBuilder(AppBuilder):
    '''
    Specialized application builder for Flask applications.
    '''

    # * method: get_routers
    def get_routers(self) -> List[ApiRouter]:
        '''
        Resolve and execute the get_routers event from the service provider.

        :return: A list of ApiRouter domain objects.
        :rtype: List[ApiRouter]
        '''

        # Resolve the get_routers event and execute it.
        get_routers_evt = self.service_provider.get_service('get_routers_evt')
        return get_routers_evt.execute()

    # * method: build_blueprint
    def build_blueprint(self, router: ApiRouter, view_func: Callable, **kwargs) -> Blueprint:
        '''
        Build a Flask Blueprint from an ApiRouter domain object.

        :param router: The ApiRouter domain object.
        :type router: ApiRouter
        :param view_func: The view function to handle requests.
        :type view_func: Callable
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A configured Flask Blueprint instance.
        :rtype: Blueprint
        '''

        # Create the Flask Blueprint.
        blueprint = Blueprint(
            router.name,
            __name__,
            url_prefix=router.prefix,
        )

        # Add routes from the ApiRouter domain object.
        for route in router.routes:
            blueprint.add_url_rule(
                route.path,
                route.id,
                methods=route.methods,
                view_func=view_func,
            )

        # Return the configured blueprint.
        return blueprint

    # * method: build_flask_app
    def build_flask_app(self, interface_id: str, view_func: Callable, swagger: bool = False, **kwargs) -> Flask:
        '''
        Build a complete Flask application with CORS and blueprints.

        :param interface_id: The interface ID to load.
        :type interface_id: str
        :param view_func: The view function to handle requests.
        :type view_func: Callable
        :param swagger: Whether to register a Swagger UI blueprint.
        :type swagger: bool
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

        # Load and register routers as blueprints.
        routers = self.get_routers()
        for router in routers:
            blueprint = self.build_blueprint(router, view_func=view_func, **kwargs)
            flask_app.register_blueprint(blueprint)

        # Optionally register the swagger blueprint.
        if swagger and hasattr(interface_context, 'create_swagger_blueprint'):
            swagger_bp = interface_context.create_swagger_blueprint(**kwargs)
            flask_app.register_blueprint(swagger_bp)

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
