"""Flask API Blueprints"""

# *** imports

# ** core
from typing import Any, Callable, Dict, List

# ** infra
from flask import Flask, Blueprint, jsonify
from flask_cors import CORS
from tiferet import TiferetAPIError
from tiferet.blueprints import core
from tiferet.contexts.app import AppSession
from tiferet.contexts.cache import CacheContext
from tiferet_openapi import ApiErrorResponse, ApiRouter, create_openapi_request_context

# ** app
from ..contexts.flask import FlaskApiContext

# *** constants

# ** constant: cors_origins_const_key
CORS_ORIGINS_CONST_KEY = 'cors_origins'

# ** constant: cors_methods_const_key
CORS_METHODS_CONST_KEY = 'cors_methods'

# ** constant: cors_allow_headers_const_key
CORS_ALLOW_HEADERS_CONST_KEY = 'cors_allow_headers'

# ** constant: cors_expose_headers_const_key
CORS_EXPOSE_HEADERS_CONST_KEY = 'cors_expose_headers'

# ** constant: cors_supports_credentials_const_key
CORS_SUPPORTS_CREDENTIALS_CONST_KEY = 'cors_supports_credentials'

# ** constant: cors_max_age_const_key
CORS_MAX_AGE_CONST_KEY = 'cors_max_age'

# ** constant: cors_list_option_map
CORS_LIST_OPTION_MAP = {
    CORS_ORIGINS_CONST_KEY: 'origins',
    CORS_METHODS_CONST_KEY: 'methods',
    CORS_ALLOW_HEADERS_CONST_KEY: 'allow_headers',
    CORS_EXPOSE_HEADERS_CONST_KEY: 'expose_headers',
}

# ** constant: cors_true_values
CORS_TRUE_VALUES = (
    'true',
    '1',
    'yes',
)

# ** constant: cors_false_values
CORS_FALSE_VALUES = (
    'false',
    '0',
    'no',
)

# *** functions

# ** function: parse_cors_list_option
def parse_cors_list_option(raw_value: str) -> Any:
    '''
    Parse a comma-separated constant string into a flask-cors list/wildcard value.

    :param raw_value: The raw comma-separated constant value.
    :type raw_value: str
    :return: The wildcard string '*', a list of tokens, or None when empty.
    :rtype: Any
    '''

    # Split on commas, strip whitespace, and drop empty tokens.
    tokens = [token.strip() for token in raw_value.split(',') if token.strip()]

    # Treat an empty token list as absent.
    if not tokens:
        return None

    # Preserve flask-cors' wildcard string form for a lone '*' token.
    if tokens == ['*']:
        return '*'

    # Return the parsed token list.
    return tokens

# ** function: parse_cors_bool_option
def parse_cors_bool_option(const_key: str, raw_value: str) -> bool:
    '''
    Parse a case-insensitive boolean constant string.

    :param const_key: The constant key being parsed, for error reporting.
    :type const_key: str
    :param raw_value: The raw constant value.
    :type raw_value: str
    :return: The parsed boolean.
    :rtype: bool
    :raises ValueError: If raw_value is not a recognized boolean token.
    '''

    # Normalize the raw value for case-insensitive comparison.
    normalized_value = raw_value.strip().lower()

    # Match against the recognized true/false token sets.
    if normalized_value in CORS_TRUE_VALUES:
        return True
    if normalized_value in CORS_FALSE_VALUES:
        return False

    # Raise if the value is not a recognized boolean token.
    raise ValueError(f'Invalid boolean value for constant {const_key!r}: {raw_value!r}')

# ** function: parse_cors_max_age_option
def parse_cors_max_age_option(const_key: str, raw_value: str) -> int:
    '''
    Parse a non-negative integer constant string.

    :param const_key: The constant key being parsed, for error reporting.
    :type const_key: str
    :param raw_value: The raw constant value.
    :type raw_value: str
    :return: The parsed non-negative integer.
    :rtype: int
    :raises ValueError: If raw_value is not a non-negative integer.
    '''

    # Attempt to parse the value as an integer, rejecting negatives.
    try:
        parsed_value = int(raw_value)
        if parsed_value < 0:
            raise ValueError
    except (TypeError, ValueError) as exception:
        raise ValueError(f'Invalid non-negative integer for constant {const_key!r}: {raw_value!r}') from exception

    # Return the parsed value.
    return parsed_value

# ** function: parse_cors_options
def parse_cors_options(constants: Dict[str, str]) -> dict:
    '''
    Parse the closed set of cors_* session constants into flask-cors kwargs.

    :param constants: The resolved AppSession constants map.
    :type constants: Dict[str, str]
    :return: A kwargs dict suitable for flask_cors.CORS(**options); empty when
        no recognized keys are set (today's wide-open default applies).
    :rtype: dict
    '''

    # Accumulate recognized options; unknown keys are ignored.
    options = {}

    # Parse the four comma-separated list options.
    for const_key, kwarg_name in CORS_LIST_OPTION_MAP.items():
        raw_value = constants.get(const_key)
        if not raw_value:
            continue
        parsed_value = parse_cors_list_option(raw_value)
        if parsed_value is not None:
            options[kwarg_name] = parsed_value

    # Parse the boolean supports_credentials option.
    raw_supports_credentials = constants.get(CORS_SUPPORTS_CREDENTIALS_CONST_KEY)
    if raw_supports_credentials is not None:
        options['supports_credentials'] = parse_cors_bool_option(
            CORS_SUPPORTS_CREDENTIALS_CONST_KEY,
            raw_supports_credentials,
        )

    # Parse the integer max_age option.
    raw_max_age = constants.get(CORS_MAX_AGE_CONST_KEY)
    if raw_max_age is not None:
        options['max_age'] = parse_cors_max_age_option(CORS_MAX_AGE_CONST_KEY, raw_max_age)

    # Return the parsed CORS kwargs.
    return options

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

# ** function: handle_tiferet_api_error
def handle_tiferet_api_error(api_error: TiferetAPIError) -> Any:
    '''
    Map a raised TiferetAPIError into a structured JSON error response.

    :param api_error: The raised TiferetAPIError carrying the resolved status code.
    :type api_error: TiferetAPIError
    :return: A tuple of the JSON error response and its HTTP status code.
    :rtype: Any
    '''

    # Build the ApiErrorResponse body from the raised error.
    payload = ApiErrorResponse(error=api_error.name, message=api_error.message or '')

    # Return the JSON response with the mapped HTTP status code.
    return jsonify(payload.model_dump()), getattr(api_error, 'status_code', 500)

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
    Flask app, registers the TiferetAPIError errorhandler, and registers
    routers as blueprints.

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

    # Create the Flask application with CORS parsed from the session constants.
    flask_app = Flask(__name__)
    CORS(flask_app, **parse_cors_options(app_session.constants))

    # Register the TiferetAPIError errorhandler so uncaught catalogued errors
    # surface as structured JSON instead of Flask's default 500 HTML page.
    flask_app.register_error_handler(TiferetAPIError, handle_tiferet_api_error)

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
