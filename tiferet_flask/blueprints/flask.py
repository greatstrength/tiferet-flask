"""Flask API Blueprints"""

# *** imports

# ** core
from typing import Any, Callable, List

# ** infra
from flask import Flask, Blueprint
from flask_cors import CORS
from tiferet.blueprints import core
from tiferet.contexts.app import AppSession
from tiferet.contexts.cache import CacheContext
from tiferet_openapi import ApiRouter, create_openapi_request_context

# ** app
from ..contexts.flask import FlaskApiContext


# *** functions

# ** function: get_route_handler
def get_route_handler(get_dependency: Callable) -> Callable:
    '''
    Build a route-lookup closure that resolves the get-route event via DI.

    :param get_dependency: The DI resolution handler.
    :type get_dependency: Callable
    :return: A callable that retrieves a route by endpoint.
    :rtype: Callable
    '''

    # Return the handler closure bound to the resolver.
    def handler(**kwargs) -> Any:

        # Resolve and execute the get-route event.
        get_route_evt = get_dependency('get_route_evt', 'app')
        return get_route_evt.execute(**kwargs)

    # Return the closure.
    return handler


# ** function: get_status_code_handler
def get_status_code_handler(get_dependency: Callable) -> Callable:
    '''
    Build a status-code-lookup closure that resolves the get-status-code event via DI.

    :param get_dependency: The DI resolution handler.
    :type get_dependency: Callable
    :return: A callable that retrieves an HTTP status code by error code.
    :rtype: Callable
    '''

    # Return the handler closure bound to the resolver.
    def handler(**kwargs) -> Any:

        # Resolve and execute the get-status-code event.
        get_status_code_evt = get_dependency('get_status_code_evt', 'app')
        return get_status_code_evt.execute(**kwargs)

    # Return the closure.
    return handler


# ** function: get_routers_handler
def get_routers_handler(get_dependency: Callable) -> Callable:
    '''
    Build a routers-lookup closure that resolves the get-routers event via DI.

    :param get_dependency: The DI resolution handler.
    :type get_dependency: Callable
    :return: A callable that retrieves the configured routers.
    :rtype: Callable
    '''

    # Return the handler closure bound to the resolver.
    def handler(**kwargs) -> Any:

        # Resolve and execute the get-routers event.
        get_routers_evt = get_dependency('get_routers_evt', 'app')
        return get_routers_evt.execute(**kwargs)

    # Return the closure.
    return handler


# *** blueprints

# ** blueprint: build_flask_session_context
def build_flask_session_context(app_session: AppSession,
        cache: CacheContext,
        create_request_handler: Callable = None,
        **extra_kwargs) -> FlaskApiContext:
    '''
    Build a fully wired FlaskApiContext from a resolved app session.

    Parallel to tiferet_openapi.blueprints.openapi.build_openapi_session_context,
    but realizes FlaskApiContext directly so Flask-specific methods such as
    create_swagger_blueprint remain available on the composed context.

    :param app_session: The resolved app session definition.
    :type app_session: AppSession
    :param cache: The pre-built shared cache context.
    :type cache: CacheContext
    :param create_request_handler: Optional request-construction handler;
        defaults to create_openapi_request_context when omitted.
    :type create_request_handler: Callable
    :param extra_kwargs: Additional keyword arguments forwarded to the
        context constructor.
    :type extra_kwargs: dict
    :return: The wired Flask API context.
    :rtype: FlaskApiContext
    '''

    # Build the app service container and compose the feature-level resolver.
    app_container = core.build_app_service_container(cache, app_session)
    resolver = core.build_service_resolver(app_container)

    # Delegate handler wiring, collaborator resolution, and construction.
    return core.compose_session_context(
        FlaskApiContext,
        app_session,
        cache,
        app_container,
        resolver,
        create_request_handler=create_request_handler or create_openapi_request_context,
        response_handler=core.response_handler,
        get_route_handler=get_route_handler(resolver.get_dependency),
        get_status_code_handler=get_status_code_handler(resolver.get_dependency),
        get_routers_handler=get_routers_handler(resolver.get_dependency),
        **extra_kwargs,
    )


# ** blueprint: get_routers
def get_routers(interface_context: FlaskApiContext) -> List[ApiRouter]:
    '''
    Retrieve the configured routers from the composed Flask API context.

    :param interface_context: The realized Flask API context.
    :type interface_context: FlaskApiContext
    :return: A list of ApiRouter domain objects.
    :rtype: List[ApiRouter]
    '''

    # Retrieve the routers from the interface context.
    return interface_context.get_routers()


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

    Loads the app session via core.build_cache/core.get_app_session, composes
    the FlaskApiContext via build_flask_session_context, builds a CORS-enabled
    Flask app, and registers routers as blueprints.

    :param interface_id: The interface ID to load.
    :type interface_id: str
    :param view_func: The view function to handle requests.
    :type view_func: Callable
    :param swagger: Whether to register a Swagger UI blueprint.
    :type swagger: bool
    :param parameters: Additional keyword arguments passed to core.get_app_session.
    :type parameters: dict
    :return: A configured Flask application instance.
    :rtype: Flask
    '''

    # Build the bootstrap cache and resolve the app session.
    cache = core.build_cache()
    app_session = core.get_app_session(interface_id, cache, **parameters)

    # Compose the Flask API context from the resolved app session.
    interface_context = build_flask_session_context(app_session, cache)

    # Create the Flask application with CORS.
    flask_app = Flask(__name__)
    CORS(flask_app)

    # Load and register routers as blueprints.
    routers = get_routers(interface_context)
    for router in routers:
        blueprint = build_blueprint(router, view_func=view_func)
        flask_app.register_blueprint(blueprint)

    # Optionally register the swagger blueprint.
    if swagger:
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
