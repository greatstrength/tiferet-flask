"""Flask API Blueprints"""

# *** imports

# ** core
from typing import Callable, List

# ** infra
from flask import Flask, Blueprint
from flask_cors import CORS
from tiferet_openapi import ApiRouter
from tiferet.blueprints.main import (
    resolve_interface,
    realize_interface,
)


# *** blueprints

# ** blueprint: get_routers
def get_routers(interface_context) -> List[ApiRouter]:
    '''
    Execute the get_routers event from the interface context.

    :param interface_context: The realized interface context with a get_routers_evt attribute.
    :type interface_context: AppInterfaceContext
    :return: A list of ApiRouter domain objects.
    :rtype: List[ApiRouter]
    '''

    # Execute the get_routers handler from the interface context.
    return interface_context.get_routers_handler()


# ** blueprint: build_blueprint
def build_blueprint(router: ApiRouter, view_func: Callable, **kwargs) -> Blueprint:
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


# ** blueprint: build_flask_app
def build_flask_app(interface_id: str, view_func: Callable, swagger: bool = False, **parameters) -> Flask:
    '''
    Build a complete Flask application with CORS and blueprints.

    Resolves the interface via tiferet.blueprints.main, realizes it,
    builds CORS-enabled Flask app, and registers routers as blueprints.

    :param interface_id: The interface ID to load.
    :type interface_id: str
    :param view_func: The view function to handle requests.
    :type view_func: Callable
    :param swagger: Whether to register a Swagger UI blueprint.
    :type swagger: bool
    :param parameters: Additional keyword arguments passed to resolve_interface.
    :type parameters: dict
    :return: A configured Flask application instance.
    :rtype: Flask
    '''

    # Resolve the interface definition.
    app_interface, _ = resolve_interface(interface_id, **parameters)

    # Realize the app interface context.
    interface_context = realize_interface(app_interface, interface_id)

    # Create the Flask application with CORS.
    flask_app = Flask(__name__)
    CORS(flask_app)

    # Load and register routers as blueprints.
    routers = get_routers(interface_context)
    for router in routers:
        blueprint = build_blueprint(router, view_func=view_func)
        flask_app.register_blueprint(blueprint)

    # Optionally register the swagger blueprint.
    if swagger and hasattr(interface_context, 'create_swagger_blueprint'):
        swagger_bp = interface_context.create_swagger_blueprint()
        flask_app.register_blueprint(swagger_bp)

    # Return the assembled Flask application.
    return flask_app


# ** blueprint: run
def run(interface_id: str, view_func: Callable, **parameters) -> Flask:
    '''
    Build and return a ready-to-serve Flask application.

    Convenience alias for build_flask_app.

    :param interface_id: The interface ID to load.
    :type interface_id: str
    :param view_func: The view function to handle requests.
    :type view_func: Callable
    :param parameters: Additional keyword arguments.
    :type parameters: dict
    :return: A configured Flask application instance.
    :rtype: Flask
    '''

    # Build and return the Flask application.
    return build_flask_app(interface_id, view_func, **parameters)
