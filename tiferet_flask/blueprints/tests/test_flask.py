'''Flask API Blueprint Tests'''

# *** imports

# ** core
import inspect
from unittest import mock

# ** infra
import pytest
from flask import Blueprint, Flask
from tiferet import use_tester
from tiferet.blueprints import core
from tiferet.contexts.app import AppSession
from tiferet.contexts.cache import CacheContext
from tiferet_openapi import ApiRoute, ApiRouter, create_openapi_request_context

# ** app
from .. import flask as flask_blueprint_module
from ..flask import (
    build_blueprint,
    build_flask_app,
    build_flask_session_context,
    get_route_handler,
    get_routers,
    get_routers_handler,
    get_status_code_handler,
)
from ...assets.core import (
    APP_FLAG,
    GET_ROUTE_EVT_SERVICE_ID,
    GET_ROUTERS_EVT_SERVICE_ID,
    GET_STATUS_CODE_EVT_SERVICE_ID,
)
from ...assets.swagger import (
    SWAGGER_BLUEPRINT_NAME,
    SWAGGER_URL_PREFIX,
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

    # Flask add_url_rule reads required_methods during blueprint registration.
    view_func = mock.Mock()
    view_func.required_methods = set()
    return view_func

# ** fixture: app_session
@pytest.fixture
def app_session() -> AppSession:
    '''
    AppSession bound to the Flask API context under test.

    :return: An AppSession domain object.
    :rtype: AppSession
    '''

    return AppSession(id='test_flask', name='Test Flask API')

# ** fixture: cache
@pytest.fixture
def cache() -> CacheContext:
    '''
    Bootstrap cache pre-seeded with all framework defaults.

    :return: A CacheContext seeded by core.build_cache.
    :rtype: CacheContext
    '''

    return core.build_cache()

# *** tests

# ** test: build_blueprint_single_route
def test_build_blueprint_single_route(sample_router: ApiRouter, mock_view_func: mock.Mock):
    '''
    Test build_blueprint creates a Blueprint with a single route.
    '''

    # Build the blueprint.
    bp = build_blueprint(sample_router, mock_view_func)

    # Assert it is a Blueprint with the expected name and prefix.
    assert isinstance(bp, Blueprint)
    assert bp.name == 'calc'
    assert bp.url_prefix == '/calc'

    # Assert the blueprint has one deferred function (the route).
    assert len(bp.deferred_functions) == 1

# ** test: build_blueprint_multiple_routes
def test_build_blueprint_multiple_routes(multi_route_router: ApiRouter, mock_view_func: mock.Mock):
    '''
    Test build_blueprint creates a Blueprint with multiple routes.
    '''

    # Build the blueprint.
    bp = build_blueprint(multi_route_router, mock_view_func)

    # Assert it is a Blueprint with the expected name.
    assert isinstance(bp, Blueprint)
    assert bp.name == 'calc'

    # Assert the blueprint has three deferred functions (one per route).
    assert len(bp.deferred_functions) == 3

# ** test: build_blueprint_no_prefix
def test_build_blueprint_no_prefix(mock_view_func: mock.Mock):
    '''
    Test build_blueprint handles a router with no prefix.
    '''

    # Create a router with no prefix.
    router = ApiRouter(
        name='health',
        prefix=None,
        routes=[
            ApiRoute(id='ping', endpoint='health.ping', path='/ping', methods=['GET'], status_code=200),
        ],
    )

    # Build the blueprint.
    bp = build_blueprint(router, mock_view_func)

    # Assert prefix is None.
    assert bp.name == 'health'
    assert bp.url_prefix is None

# ** test: build_flask_app_module_has_no_generate_spec_reference
def test_build_flask_app_module_has_no_generate_spec_reference():
    '''
    Assert the Flask blueprint module does not reference generate_spec.
    '''

    # Read the Flask blueprint module source.
    source = inspect.getsource(flask_blueprint_module)

    # Assert swagger spec generation stays on FlaskApiContext.create_swagger_blueprint.
    assert 'generate_spec' not in source

# *** testers

# ** tester: test_get_routers
@use_tester(
    type='generic',
    target_cls=get_routers,
)
class TestGetRouters:
    '''
    Bound generic tester for get_routers.
    '''

    # * test: returns_configured_routers
    def test_returns_configured_routers(self, sample_router: ApiRouter):
        '''
        Test get_routers returns routers from the composed context.

        :param sample_router: The sample router returned by the context.
        :type sample_router: ApiRouter
        '''

        # Mock a composed context exposing get_routers.
        interface_context = mock.Mock(spec=FlaskApiContext)
        interface_context.get_routers.return_value = [sample_router]

        # Retrieve the routers from the composed context.
        result = get_routers(interface_context)

        # Assert the context method is called and the routers pass through.
        interface_context.get_routers.assert_called_once_with()
        assert result == [sample_router]

    # * test: empty
    def test_empty(self):
        '''
        Test get_routers returns an empty list when the context has no routers.
        '''

        # Mock a composed context with no routers.
        interface_context = mock.Mock(spec=FlaskApiContext)
        interface_context.get_routers.return_value = []

        # Retrieve the routers from the composed context.
        result = get_routers(interface_context)

        # Assert an empty catalog is returned unchanged.
        interface_context.get_routers.assert_called_once_with()
        assert result == []

# ** tester: test_get_route_handler
@use_tester(
    type='generic',
    target_cls=get_route_handler,
)
class TestGetRouteHandler:
    '''
    Bound generic tester for get_route_handler.
    '''

    # * test: resolves_service_id_and_app_flag
    def test_resolves_service_id_and_app_flag(self):
        '''
        Test get_route_handler resolves the event via DI and executes it.
        '''

        # Stub the DI resolver to return a mock get-route event.
        event = mock.Mock()
        event.execute = mock.Mock(return_value='route')
        get_dependency = mock.Mock(return_value=event)

        # Invoke the handler closure.
        result = get_route_handler(get_dependency)(id='calc.add')

        # Assert DI resolution, event execution, and passthrough.
        get_dependency.assert_called_once_with(GET_ROUTE_EVT_SERVICE_ID, APP_FLAG)
        event.execute.assert_called_once_with(id='calc.add')
        assert result == 'route'

# ** tester: test_get_status_code_handler
@use_tester(
    type='generic',
    target_cls=get_status_code_handler,
)
class TestGetStatusCodeHandler:
    '''
    Bound generic tester for get_status_code_handler.
    '''

    # * test: resolves_service_id_and_app_flag
    def test_resolves_service_id_and_app_flag(self):
        '''
        Test get_status_code_handler resolves the event via DI and executes it.
        '''

        # Stub the DI resolver to return a mock get-status-code event.
        event = mock.Mock()
        event.execute = mock.Mock(return_value=400)
        get_dependency = mock.Mock(return_value=event)

        # Invoke the handler closure.
        result = get_status_code_handler(get_dependency)(error_code='DIVISION_BY_ZERO')

        # Assert DI resolution, event execution, and passthrough.
        get_dependency.assert_called_once_with(GET_STATUS_CODE_EVT_SERVICE_ID, APP_FLAG)
        event.execute.assert_called_once_with(error_code='DIVISION_BY_ZERO')
        assert result == 400

# ** tester: test_get_routers_handler
@use_tester(
    type='generic',
    target_cls=get_routers_handler,
)
class TestGetRoutersHandler:
    '''
    Bound generic tester for get_routers_handler.
    '''

    # * test: resolves_service_id_and_app_flag
    def test_resolves_service_id_and_app_flag(self):
        '''
        Test get_routers_handler resolves the event via DI and executes it.
        '''

        # Stub the DI resolver to return a mock get-routers event.
        event = mock.Mock()
        event.execute = mock.Mock(return_value=[])
        get_dependency = mock.Mock(return_value=event)

        # Invoke the handler closure with no kwargs.
        result = get_routers_handler(get_dependency)()

        # Assert DI resolution, event execution, and passthrough.
        get_dependency.assert_called_once_with(GET_ROUTERS_EVT_SERVICE_ID, APP_FLAG)
        event.execute.assert_called_once_with()
        assert result == []

# ** tester: test_build_flask_session_context
@use_tester(
    type='generic',
    target_cls=build_flask_session_context,
)
class TestBuildFlaskSessionContext:
    '''
    Bound generic tester for build_flask_session_context.
    '''

    # * test: constructs_wired_flask_api_context
    def test_constructs_wired_flask_api_context(
            self,
            session,
            app_session: AppSession,
            cache: CacheContext,
        ):
        '''
        Test that build_flask_session_context constructs a wired FlaskApiContext.

        :param session: A fresh generic test session.
        :type session: TestSessionContext
        :param app_session: The AppSession domain object.
        :type app_session: AppSession
        :param cache: The bootstrap cache.
        :type cache: CacheContext
        '''

        # Build the session context from cache and session only.
        result = session.given(
            app_session=app_session,
            cache=cache,
        ).run(target=build_flask_session_context)

        # Assert the constructed context, bound session, and default handlers.
        assert isinstance(result, FlaskApiContext)
        assert result.domain is app_session
        assert result._create_request is create_openapi_request_context
        assert result._build_response is core.response_handler
        assert callable(result._get_route)
        assert callable(result._get_status_code)
        assert callable(result._get_routers)

    # * test: accepts_custom_request_handler
    def test_accepts_custom_request_handler(
            self,
            session,
            app_session: AppSession,
            cache: CacheContext,
        ):
        '''
        Test that a custom create_request_handler is wired onto the context.

        :param session: A fresh generic test session.
        :type session: TestSessionContext
        :param app_session: The AppSession domain object.
        :type app_session: AppSession
        :param cache: The bootstrap cache.
        :type cache: CacheContext
        '''

        # Pass a custom request-construction handler.
        custom_handler = mock.Mock(name='custom_request_handler')
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
    Bound generic tester for build_flask_app.
    '''

    # * test: registers_blueprints
    def test_registers_blueprints(
            self,
            sample_router: ApiRouter,
            mock_view_func: mock.Mock,
        ):
        '''
        Test build_flask_app registers one Flask blueprint per router.

        :param sample_router: The sample router returned by the context.
        :type sample_router: ApiRouter
        :param mock_view_func: The mock view function.
        :type mock_view_func: mock.Mock
        '''

        # Patch session assembly collaborators.
        mock_cache = mock.Mock()
        mock_app_session = mock.Mock()
        mock_context = mock.Mock(spec=FlaskApiContext)
        mock_context.get_routers.return_value = [sample_router]

        with mock.patch(
            'tiferet_flask.blueprints.flask.core.build_cache',
            return_value=mock_cache,
        ) as mock_build_cache, mock.patch(
            'tiferet_flask.blueprints.flask.core.get_app_session',
            return_value=mock_app_session,
        ) as mock_get_app_session, mock.patch(
            'tiferet_flask.blueprints.flask.build_flask_session_context',
            return_value=mock_context,
        ) as mock_build_session_context:

            # Build the Flask application.
            result = build_flask_app('test_flask', mock_view_func)

        # Assert session assembly and blueprint registration.
        mock_build_cache.assert_called_once_with()
        mock_get_app_session.assert_called_once_with('test_flask', mock_cache)
        mock_build_session_context.assert_called_once_with(mock_app_session, mock_cache)
        assert isinstance(result, Flask)
        assert 'calc' in result.blueprints
        assert result.blueprints['calc'].url_prefix == '/calc'

    # * test: with_swagger
    def test_with_swagger(
            self,
            sample_router: ApiRouter,
            mock_view_func: mock.Mock,
        ):
        '''
        Test swagger=True registers create_swagger_blueprint once with no extra kwargs.

        :param sample_router: The sample router returned by the context.
        :type sample_router: ApiRouter
        :param mock_view_func: The mock view function.
        :type mock_view_func: mock.Mock
        '''

        # Patch session assembly collaborators.
        mock_cache = mock.Mock()
        mock_app_session = mock.Mock()
        mock_context = mock.Mock(spec=FlaskApiContext)
        mock_context.get_routers.return_value = [sample_router]
        swagger_bp = Blueprint(
            SWAGGER_BLUEPRINT_NAME,
            __name__,
            url_prefix=SWAGGER_URL_PREFIX,
        )
        mock_context.create_swagger_blueprint.return_value = swagger_bp

        with mock.patch(
            'tiferet_flask.blueprints.flask.core.build_cache',
            return_value=mock_cache,
        ), mock.patch(
            'tiferet_flask.blueprints.flask.core.get_app_session',
            return_value=mock_app_session,
        ), mock.patch(
            'tiferet_flask.blueprints.flask.build_flask_session_context',
            return_value=mock_context,
        ):

            # Build the Flask application with swagger enabled.
            result = build_flask_app('test_flask', mock_view_func, swagger=True)

        # Assert the swagger blueprint is created once with no extra kwargs and registered.
        mock_context.create_swagger_blueprint.assert_called_once_with()
        assert SWAGGER_BLUEPRINT_NAME in result.blueprints
        assert result.blueprints[SWAGGER_BLUEPRINT_NAME] is swagger_bp

    # * test: without_swagger
    def test_without_swagger(
            self,
            sample_router: ApiRouter,
            mock_view_func: mock.Mock,
        ):
        '''
        Test swagger=False does not create or register the swagger blueprint.

        :param sample_router: The sample router returned by the context.
        :type sample_router: ApiRouter
        :param mock_view_func: The mock view function.
        :type mock_view_func: mock.Mock
        '''

        # Patch session assembly collaborators.
        mock_cache = mock.Mock()
        mock_app_session = mock.Mock()
        mock_context = mock.Mock(spec=FlaskApiContext)
        mock_context.get_routers.return_value = [sample_router]

        with mock.patch(
            'tiferet_flask.blueprints.flask.core.build_cache',
            return_value=mock_cache,
        ), mock.patch(
            'tiferet_flask.blueprints.flask.core.get_app_session',
            return_value=mock_app_session,
        ), mock.patch(
            'tiferet_flask.blueprints.flask.build_flask_session_context',
            return_value=mock_context,
        ):

            # Build the Flask application with swagger disabled.
            result = build_flask_app('test_flask', mock_view_func, swagger=False)

        # Assert the swagger blueprint is neither created nor registered.
        mock_context.create_swagger_blueprint.assert_not_called()
        assert SWAGGER_BLUEPRINT_NAME not in result.blueprints

    # * test: extra_parameters_go_to_get_app_session
    def test_extra_parameters_go_to_get_app_session(
            self,
            sample_router: ApiRouter,
            mock_view_func: mock.Mock,
        ):
        '''
        Test extra kwargs are passed only to core.get_app_session.

        :param sample_router: The sample router returned by the context.
        :type sample_router: ApiRouter
        :param mock_view_func: The mock view function.
        :type mock_view_func: mock.Mock
        '''

        # Patch session assembly collaborators.
        mock_cache = mock.Mock()
        mock_app_session = mock.Mock()
        mock_context = mock.Mock(spec=FlaskApiContext)
        mock_context.get_routers.return_value = [sample_router]
        swagger_bp = Blueprint(
            SWAGGER_BLUEPRINT_NAME,
            __name__,
            url_prefix=SWAGGER_URL_PREFIX,
        )
        mock_context.create_swagger_blueprint.return_value = swagger_bp

        with mock.patch(
            'tiferet_flask.blueprints.flask.core.build_cache',
            return_value=mock_cache,
        ), mock.patch(
            'tiferet_flask.blueprints.flask.core.get_app_session',
            return_value=mock_app_session,
        ) as mock_get_app_session, mock.patch(
            'tiferet_flask.blueprints.flask.build_flask_session_context',
            return_value=mock_context,
        ) as mock_build_session_context:

            # Build the Flask application with an extra parameter and swagger.
            build_flask_app(
                'test_flask',
                mock_view_func,
                swagger=True,
                extra_param='should_not_leak',
            )

        # Assert extra kwargs reach get_app_session only.
        mock_get_app_session.assert_called_once_with(
            'test_flask',
            mock_cache,
            extra_param='should_not_leak',
        )
        mock_build_session_context.assert_called_once_with(mock_app_session, mock_cache)
        mock_context.create_swagger_blueprint.assert_called_once_with()

    # * test: swagger_register_no_op_when_name_already_taken
    def test_swagger_register_no_op_when_name_already_taken(
            self,
            sample_route: ApiRoute,
            mock_view_func: mock.Mock,
        ):
        '''
        Test swagger registration is skipped when the blueprint name is taken.

        :param sample_route: A sample route for the colliding router.
        :type sample_route: ApiRoute
        :param mock_view_func: The mock view function.
        :type mock_view_func: mock.Mock
        '''

        # Register a router that already occupies the swagger blueprint name.
        collision_router = ApiRouter(
            name=SWAGGER_BLUEPRINT_NAME,
            prefix='/already-taken',
            routes=[sample_route],
        )
        mock_cache = mock.Mock()
        mock_app_session = mock.Mock()
        mock_context = mock.Mock(spec=FlaskApiContext)
        mock_context.get_routers.return_value = [collision_router]
        swagger_bp = Blueprint(
            SWAGGER_BLUEPRINT_NAME,
            __name__,
            url_prefix=SWAGGER_URL_PREFIX,
        )
        mock_context.create_swagger_blueprint.return_value = swagger_bp

        with mock.patch(
            'tiferet_flask.blueprints.flask.core.build_cache',
            return_value=mock_cache,
        ), mock.patch(
            'tiferet_flask.blueprints.flask.core.get_app_session',
            return_value=mock_app_session,
        ), mock.patch(
            'tiferet_flask.blueprints.flask.build_flask_session_context',
            return_value=mock_context,
        ):

            # Build the Flask application with swagger enabled.
            result = build_flask_app('test_flask', mock_view_func, swagger=True)

        # Assert create_swagger_blueprint is called but the existing blueprint remains.
        mock_context.create_swagger_blueprint.assert_called_once_with()
        assert result.blueprints[SWAGGER_BLUEPRINT_NAME].url_prefix == '/already-taken'
        assert result.blueprints[SWAGGER_BLUEPRINT_NAME] is not swagger_bp
