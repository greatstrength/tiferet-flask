# *** imports

# ** core
from unittest import mock

# ** infra
import pytest
from flask import Flask, Blueprint
from tiferet import TiferetAPIError, TiferetError, use_tester
from tiferet.blueprints import core
from tiferet.contexts.cache import CacheContext
from tiferet.domain import AppSession
from tiferet_openapi import ApiErrorResponse, ApiRoute, ApiRouter, create_openapi_request_context

# ** app
from ..flask import (
    build_blueprint,
    build_flask_app,
    build_flask_session_context,
    get_routers,
    handle_tiferet_api_error,
    run,
)
from ...contexts.flask import FlaskApiContext

# *** fixtures

# ** fixture: sample_route
@pytest.fixture
def sample_route() -> ApiRoute:
    '''
    Fixture to provide a sample ApiRoute.
    '''

    return ApiRoute(
        id='add',
        endpoint='calc.add',
        path='/add',
        methods=['POST'],
        status_code=200,
    )

# ** fixture: sample_router
@pytest.fixture
def sample_router(sample_route: ApiRoute) -> ApiRouter:
    '''
    Fixture to provide a sample ApiRouter with one route.
    '''

    return ApiRouter(
        name='calc',
        prefix='/calc',
        routes=[sample_route],
    )

# ** fixture: multi_route_router
@pytest.fixture
def multi_route_router() -> ApiRouter:
    '''
    Fixture to provide an ApiRouter with multiple routes.
    '''

    return ApiRouter(
        name='calc',
        prefix='/calc',
        routes=[
            ApiRoute(id='add', endpoint='calc.add', path='/add', methods=['POST'], status_code=200),
            ApiRoute(id='subtract', endpoint='calc.subtract', path='/subtract', methods=['POST'], status_code=200),
            ApiRoute(id='multiply', endpoint='calc.multiply', path='/multiply', methods=['GET', 'POST'], status_code=200),
        ],
    )

# ** fixture: mock_view_func
@pytest.fixture
def mock_view_func() -> mock.Mock:
    '''
    Fixture to provide a mock view function.
    '''

    # Create a mock with required_methods set for Flask add_url_rule compatibility.
    view_func = mock.Mock()
    view_func.required_methods = set()

    return view_func

# ** fixture: app_session
@pytest.fixture
def app_session() -> AppSession:
    '''
    Fixture to provide the AppSession resolved by build_flask_session_context.
    '''

    return AppSession(id='test_flask', name='Test Flask API')

# ** fixture: cache
@pytest.fixture
def cache() -> CacheContext:
    '''
    Fixture to provide the bootstrap cache pre-seeded with framework defaults.
    '''

    return core.build_cache()

# ** fixture: sample_api_error
@pytest.fixture
def sample_api_error() -> TiferetAPIError:
    '''
    Fixture to provide a TiferetAPIError already resolved with a status code,
    matching what OpenApiSessionContext.handle_error attaches.
    '''

    api_error = TiferetAPIError('DIVISION_BY_ZERO', message='Cannot divide by zero.', name='DIVISION_BY_ZERO')
    api_error.status_code = 400

    return api_error

# *** testers

# ** tester: test_build_blueprint
@use_tester(
    type='generic',
    target_cls=build_blueprint,
)
class TestBuildBlueprint:
    '''
    Generic tester for build_blueprint.
    '''

    # * test: single_route
    def test_build_blueprint_single_route(
            self,
            session,
            sample_router: ApiRouter,
            mock_view_func: mock.Mock,
        ) -> None:
        '''
        Verify build_blueprint creates a Blueprint with a single route.
        '''

        # Exercise build_blueprint with a single-route router.
        result = session.given(router=sample_router, view_func=mock_view_func).run(target=build_blueprint)

        # Assert it is a Blueprint with the expected name, prefix, and route count.
        assert isinstance(result, Blueprint)
        assert result.name == 'calc'
        assert result.url_prefix == '/calc'
        assert len(result.deferred_functions) == 1

    # * test: multiple_routes
    def test_build_blueprint_multiple_routes(
            self,
            session,
            multi_route_router: ApiRouter,
            mock_view_func: mock.Mock,
        ) -> None:
        '''
        Verify build_blueprint creates a Blueprint with multiple routes.
        '''

        # Exercise build_blueprint with a multi-route router.
        result = session.given(router=multi_route_router, view_func=mock_view_func).run(target=build_blueprint)

        # Assert one deferred function per route.
        assert isinstance(result, Blueprint)
        assert result.name == 'calc'
        assert len(result.deferred_functions) == 3

    # * test: no_prefix
    def test_build_blueprint_no_prefix(
            self,
            session,
            mock_view_func: mock.Mock,
        ) -> None:
        '''
        Verify build_blueprint handles a router with no prefix.
        '''

        # Build a router with no prefix.
        router = ApiRouter(
            name='health',
            prefix=None,
            routes=[
                ApiRoute(id='ping', endpoint='health.ping', path='/ping', methods=['GET'], status_code=200),
            ],
        )

        # Exercise build_blueprint with the no-prefix router.
        result = session.given(router=router, view_func=mock_view_func).run(target=build_blueprint)

        # Assert the prefix is None.
        assert result.name == 'health'
        assert result.url_prefix is None

# ** tester: test_get_routers
@use_tester(
    type='generic',
    target_cls=get_routers,
)
class TestGetRouters:
    '''
    Generic tester for get_routers.
    '''

    # * test: returns_configured_routers
    def test_get_routers_returns_configured_routers(
            self,
            session,
            sample_router: ApiRouter,
        ) -> None:
        '''
        Verify get_routers calls get_routers() on the interface context, not
        get_routers_handler().
        '''

        # Build a mock interface context exposing get_routers().
        mock_context = mock.Mock()
        mock_context.get_routers = mock.Mock(return_value=[sample_router])

        # Exercise get_routers against the mock interface context.
        result = session.given(interface_context=mock_context).run(target=get_routers)

        # Assert the handler was called and the router list is returned.
        mock_context.get_routers.assert_called_once_with()
        assert result == [sample_router]

    # * test: empty
    def test_get_routers_empty(self, session) -> None:
        '''
        Verify get_routers returns an empty list when no routers are configured.
        '''

        # Build a mock interface context with no routers.
        mock_context = mock.Mock()
        mock_context.get_routers = mock.Mock(return_value=[])

        # Exercise get_routers against the mock interface context.
        result = session.given(interface_context=mock_context).run(target=get_routers)

        # Assert the result is empty.
        assert result == []

# ** tester: test_handle_tiferet_api_error
@use_tester(
    type='generic',
    target_cls=handle_tiferet_api_error,
)
class TestHandleTiferetApiError:
    '''
    Generic tester for handle_tiferet_api_error.
    '''

    # * test: maps_error_and_message_with_status_code
    def test_handle_tiferet_api_error_maps_body_and_status(
            self,
            session,
            sample_api_error: TiferetAPIError,
        ) -> None:
        '''
        Verify handle_tiferet_api_error returns an ApiErrorResponse-shaped
        JSON body and the status code attached to the error.
        '''

        # Exercise handle_tiferet_api_error with a resolved TiferetAPIError.
        flask_app = Flask(__name__)
        with flask_app.test_request_context():
            response, status_code = session.given(api_error=sample_api_error).run(target=handle_tiferet_api_error)

        # Assert the JSON body validates as an ApiErrorResponse and the status is preserved.
        body = response.get_json()
        ApiErrorResponse(**body)
        assert body == {'error': 'DIVISION_BY_ZERO', 'message': 'Cannot divide by zero.'}
        assert status_code == 400

    # * test: defaults_status_code_when_missing
    def test_handle_tiferet_api_error_defaults_status_code(self, session) -> None:
        '''
        Verify handle_tiferet_api_error defaults to HTTP 500 when the error
        was never resolved through OpenApiSessionContext.handle_error.
        '''

        # Build a TiferetAPIError with no status_code attribute attached.
        unresolved_error = TiferetAPIError('UNRESOLVED_ERROR', message='Something broke.')

        # Exercise handle_tiferet_api_error with the unresolved error.
        flask_app = Flask(__name__)
        with flask_app.test_request_context():
            response, status_code = session.given(api_error=unresolved_error).run(target=handle_tiferet_api_error)

        # Assert the default status code and the name-falls-back-to-error_code body.
        assert response.get_json() == {'error': 'UNRESOLVED_ERROR', 'message': 'Something broke.'}
        assert status_code == 500

    # * test: defaults_empty_message
    def test_handle_tiferet_api_error_defaults_empty_message(self, session) -> None:
        '''
        Verify handle_tiferet_api_error maps a missing message to an empty string.
        '''

        # Build a TiferetAPIError with no message.
        api_error = TiferetAPIError('NO_MESSAGE_ERROR')
        api_error.status_code = 404

        # Exercise handle_tiferet_api_error with the messageless error.
        flask_app = Flask(__name__)
        with flask_app.test_request_context():
            response, status_code = session.given(api_error=api_error).run(target=handle_tiferet_api_error)

        # Assert the message defaults to an empty string.
        assert response.get_json() == {'error': 'NO_MESSAGE_ERROR', 'message': ''}
        assert status_code == 404

# ** tester: test_build_flask_session_context
@use_tester(
    type='generic',
    target_cls=build_flask_session_context,
)
class TestBuildFlaskSessionContext:
    '''
    Generic tester for build_flask_session_context.
    '''

    # * test: constructs_wired_flask_api_context
    def test_build_flask_session_context_constructs_context(
            self,
            session,
            app_session: AppSession,
            cache: CacheContext,
        ) -> None:
        '''
        Verify build_flask_session_context constructs a wired FlaskApiContext
        with the default request/response handlers (RFP-001 Risk 4).
        '''

        # Exercise build_flask_session_context with cache and session only.
        result = session.given(app_session=app_session, cache=cache).run(target=build_flask_session_context)

        # Assert the constructed context, bound domain, and default handlers.
        assert isinstance(result, FlaskApiContext)
        assert result.domain is app_session
        assert result._create_request is create_openapi_request_context
        assert result._build_response is core.response_handler
        assert callable(result._get_route)
        assert callable(result._get_status_code)
        assert callable(result._get_routers)

    # * test: accepts_custom_request_handler
    def test_build_flask_session_context_accepts_custom_request_handler(
            self,
            session,
            app_session: AppSession,
            cache: CacheContext,
        ) -> None:
        '''
        Verify build_flask_session_context accepts a custom request handler.
        '''

        # Exercise build_flask_session_context with a custom request handler.
        custom_handler = mock.Mock()
        result = session.given(
            app_session=app_session,
            cache=cache,
            create_request_handler=custom_handler,
        ).run(target=build_flask_session_context)

        # Assert the custom request handler is wired.
        assert result._create_request is custom_handler

# ** tester: test_build_flask_app
@use_tester(
    type='generic',
    target_cls=build_flask_app,
)
class TestBuildFlaskApp:
    '''
    Generic tester for build_flask_app. Patches core.build_cache,
    core.get_app_session, and build_flask_session_context directly on
    tiferet_flask.blueprints.flask.
    '''

    # * test: registers_one_blueprint_per_router
    def test_build_flask_app_registers_blueprints(
            self,
            session,
            sample_router: ApiRouter,
            mock_view_func: mock.Mock,
        ) -> None:
        '''
        Verify build_flask_app registers one Flask blueprint per router.
        '''

        # Build a mock interface context exposing the sample router.
        mock_context = mock.Mock()
        mock_context.get_routers = mock.Mock(return_value=[sample_router])
        mock_cache = mock.Mock()
        mock_app_session = mock.Mock()

        # Patch the three collaborators build_flask_app composes.
        with mock.patch('tiferet_flask.blueprints.flask.core.build_cache', return_value=mock_cache), \
             mock.patch('tiferet_flask.blueprints.flask.core.get_app_session', return_value=mock_app_session) as mock_get_app_session, \
             mock.patch('tiferet_flask.blueprints.flask.build_flask_session_context', return_value=mock_context) as mock_build_session:

            # Exercise build_flask_app.
            result = session.given(interface_id='test_interface', view_func=mock_view_func).run(target=build_flask_app)

        # Assert a Flask app was returned with the router registered.
        assert isinstance(result, Flask)
        assert 'calc' in result.blueprints

        # Assert the collaborators were composed with the resolved app session.
        mock_get_app_session.assert_called_once_with('test_interface', mock_cache)
        mock_build_session.assert_called_once_with(mock_app_session, mock_cache)

    # * test: registers_swagger_only_when_enabled
    def test_build_flask_app_with_swagger(
            self,
            session,
            mock_view_func: mock.Mock,
        ) -> None:
        '''
        Verify build_flask_app registers a Swagger blueprint only when
        swagger=True.
        '''

        # Build a mock interface context with a swagger blueprint.
        mock_swagger_bp = Blueprint('swagger', __name__, url_prefix='/docs')
        mock_context = mock.Mock()
        mock_context.get_routers = mock.Mock(return_value=[])
        mock_context.create_swagger_blueprint = mock.Mock(return_value=mock_swagger_bp)

        # Patch the three collaborators build_flask_app composes.
        with mock.patch('tiferet_flask.blueprints.flask.core.build_cache', return_value=mock.Mock()), \
             mock.patch('tiferet_flask.blueprints.flask.core.get_app_session', return_value=mock.Mock()), \
             mock.patch('tiferet_flask.blueprints.flask.build_flask_session_context', return_value=mock_context):

            # Exercise build_flask_app with swagger enabled.
            result = session.given(interface_id='test_interface', view_func=mock_view_func, swagger=True).run(target=build_flask_app)

        # Assert create_swagger_blueprint was called and registered.
        mock_context.create_swagger_blueprint.assert_called_once_with()
        assert 'swagger' in result.blueprints

    # * test: no_swagger_when_disabled
    def test_build_flask_app_without_swagger(
            self,
            session,
            mock_view_func: mock.Mock,
        ) -> None:
        '''
        Verify build_flask_app does not register Swagger when swagger=False.
        '''

        # Build a mock interface context with no routers.
        mock_context = mock.Mock()
        mock_context.get_routers = mock.Mock(return_value=[])
        mock_context.create_swagger_blueprint = mock.Mock()

        # Patch the three collaborators build_flask_app composes.
        with mock.patch('tiferet_flask.blueprints.flask.core.build_cache', return_value=mock.Mock()), \
             mock.patch('tiferet_flask.blueprints.flask.core.get_app_session', return_value=mock.Mock()), \
             mock.patch('tiferet_flask.blueprints.flask.build_flask_session_context', return_value=mock_context):

            # Exercise build_flask_app with swagger disabled.
            result = session.given(interface_id='test_interface', view_func=mock_view_func, swagger=False).run(target=build_flask_app)

        # Assert create_swagger_blueprint was not called and not registered.
        mock_context.create_swagger_blueprint.assert_not_called()
        assert 'swagger' not in result.blueprints

    # * test: extra_parameters_go_to_get_app_session
    def test_build_flask_app_extra_parameters_go_to_get_app_session(
            self,
            session,
            mock_view_func: mock.Mock,
        ) -> None:
        '''
        Verify extra **parameters route to get_app_session, not to
        create_swagger_blueprint.
        '''

        # Build a mock interface context with a swagger blueprint.
        mock_swagger_bp = Blueprint('swagger', __name__, url_prefix='/docs')
        mock_context = mock.Mock()
        mock_context.get_routers = mock.Mock(return_value=[])
        mock_context.create_swagger_blueprint = mock.Mock(return_value=mock_swagger_bp)
        mock_cache = mock.Mock()

        # Patch the three collaborators build_flask_app composes.
        with mock.patch('tiferet_flask.blueprints.flask.core.build_cache', return_value=mock_cache), \
             mock.patch('tiferet_flask.blueprints.flask.core.get_app_session', return_value=mock.Mock()) as mock_get_app_session, \
             mock.patch('tiferet_flask.blueprints.flask.build_flask_session_context', return_value=mock_context):

            # Exercise build_flask_app with an extra keyword parameter.
            session.given(
                interface_id='test_interface',
                view_func=mock_view_func,
                swagger=True,
                extra_param='should_not_leak',
            ).run(target=build_flask_app)

        # Assert the extra parameter reached get_app_session.
        mock_get_app_session.assert_called_once_with('test_interface', mock_cache, extra_param='should_not_leak')

        # Assert create_swagger_blueprint received no extra parameters.
        mock_context.create_swagger_blueprint.assert_called_once_with()

    # * test: registers_exactly_one_tiferet_api_error_handler
    def test_build_flask_app_registers_tiferet_api_error_handler(
            self,
            session,
            mock_view_func: mock.Mock,
        ) -> None:
        '''
        Verify build_flask_app registers exactly one errorhandler for
        TiferetAPIError, and none for TiferetError or bare Exception.
        '''

        # Build a mock interface context with no routers.
        mock_context = mock.Mock()
        mock_context.get_routers = mock.Mock(return_value=[])

        # Patch the three collaborators build_flask_app composes.
        with mock.patch('tiferet_flask.blueprints.flask.core.build_cache', return_value=mock.Mock()), \
             mock.patch('tiferet_flask.blueprints.flask.core.get_app_session', return_value=mock.Mock()), \
             mock.patch('tiferet_flask.blueprints.flask.build_flask_session_context', return_value=mock_context):

            # Exercise build_flask_app.
            result = session.given(interface_id='test_interface', view_func=mock_view_func).run(target=build_flask_app)

        # Assert exactly one handler is registered, bound to TiferetAPIError only.
        error_handler_spec = result.error_handler_spec[None][None]
        assert list(error_handler_spec.keys()) == [TiferetAPIError]
        assert error_handler_spec[TiferetAPIError] is handle_tiferet_api_error
        assert TiferetError not in error_handler_spec
        assert Exception not in error_handler_spec

# ** tester: test_run
@use_tester(
    type='generic',
    target_cls=run,
)
class TestRun:
    '''
    Generic tester for run, a thin alias for build_flask_app.
    '''

    # * test: delegates_to_build_flask_app
    def test_run_delegates_to_build_flask_app(
            self,
            session,
            mock_view_func: mock.Mock,
        ) -> None:
        '''
        Verify run delegates to build_flask_app.
        '''

        # Patch build_flask_app to a sentinel return value.
        with mock.patch('tiferet_flask.blueprints.flask.build_flask_app', return_value=mock.sentinel.flask_app) as mock_build_flask_app:

            # Exercise run.
            result = session.given(
                interface_id='test_interface',
                view_func=mock_view_func,
                app_yaml_file='app.yml',
            ).run(target=run)

        # Assert the delegation and the passthrough return value.
        mock_build_flask_app.assert_called_once_with('test_interface', mock_view_func, app_yaml_file='app.yml')
        assert result is mock.sentinel.flask_app
