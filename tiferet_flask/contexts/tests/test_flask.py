# *** imports

# ** core
from typing import Callable
from unittest import mock
import inspect
from pathlib import Path

# ** infra
import pytest
from flask import Flask, Blueprint
from tiferet import use_tester
from tiferet.contexts.app import AppSessionContext
from tiferet.contexts.core import BaseContext, ContextMeta
from tiferet.domain import AppSession
from tiferet_openapi import ApiRoute, ApiRouter

# ** app
from ..flask import FlaskApiContext
from .. import flask as flask_context_module
from ...assets.swagger import (
    SWAGGER_BLUEPRINT_NAME,
    SWAGGER_OPENAPI_JSON_PATH,
    SWAGGER_STATIC_FOLDER,
    SWAGGER_STATIC_URL_PATH,
    SWAGGER_UI_BUNDLE_JS_FILENAME,
    SWAGGER_UI_CSS_FILENAME,
    SWAGGER_URL_PREFIX,
)

# *** fixtures

# ** fixture: app_session
@pytest.fixture
def app_session() -> AppSession:
    '''
    AppSession bound to the Flask API context under test.

    :return: An AppSession domain object.
    :rtype: AppSession
    '''

    return AppSession(id='test_flask', name='Test Flask API')

# ** fixture: get_dependency
@pytest.fixture
def get_dependency() -> Callable:
    '''
    Mock DI resolution handler.

    :return: A mock callable.
    :rtype: Callable
    '''

    return mock.Mock()

# ** fixture: get_route_handler
@pytest.fixture
def get_route_handler() -> Callable:
    '''
    Mock route-lookup handler.

    :return: A mock callable.
    :rtype: Callable
    '''

    return mock.Mock()

# ** fixture: get_status_code_handler
@pytest.fixture
def get_status_code_handler() -> Callable:
    '''
    Mock status-code-lookup handler.

    :return: A mock callable.
    :rtype: Callable
    '''

    return mock.Mock()

# ** fixture: get_routers_handler
@pytest.fixture
def get_routers_handler() -> Callable:
    '''
    Mock routers-lookup handler.

    :return: A mock callable.
    :rtype: Callable
    '''

    return mock.Mock()

# ** fixture: sample_router
@pytest.fixture
def sample_router() -> ApiRouter:
    '''
    Sample ApiRouter used to assert get_routers passthrough.

    :return: An ApiRouter domain object.
    :rtype: ApiRouter
    '''

    return ApiRouter(
        name='calc',
        prefix='/calc',
        routes=[
            ApiRoute(
                id='add',
                endpoint='calc.add',
                path='/add',
                methods=['POST'],
                status_code=200,
            ),
        ],
    )

# ** fixture: flask_api_context
@pytest.fixture
def flask_api_context(
        app_session: AppSession,
        get_dependency: Callable,
        get_route_handler: Callable,
        get_status_code_handler: Callable,
        get_routers_handler: Callable,
    ) -> FlaskApiContext:
    '''
    FlaskApiContext bound via from_domain.

    :param app_session: The bound AppSession domain object.
    :type app_session: AppSession
    :param get_dependency: The mock DI resolution handler.
    :type get_dependency: Callable
    :param get_route_handler: The mock route-lookup handler.
    :type get_route_handler: Callable
    :param get_status_code_handler: The mock status-code-lookup handler.
    :type get_status_code_handler: Callable
    :param get_routers_handler: The mock routers-lookup handler.
    :type get_routers_handler: Callable
    :return: The FlaskApiContext instance.
    :rtype: FlaskApiContext
    '''

    return FlaskApiContext.from_domain(
        app_session,
        get_dependency=get_dependency,
        get_route_handler=get_route_handler,
        get_status_code_handler=get_status_code_handler,
        get_routers_handler=get_routers_handler,
    )

# *** tests

# ** test: flask_api_context_not_registered
def test_flask_api_context_not_registered():
    '''
    Assert FlaskApiContext omits domain_type and does not steal AppSession.
    '''

    assert 'domain_type' not in FlaskApiContext.__dict__
    assert FlaskApiContext not in ContextMeta.registry.values()
    assert BaseContext.for_domain(AppSession) is AppSessionContext
    assert 'create_docs_handler' not in FlaskApiContext.__dict__

# ** test: flask_context_module_uses_get_docs_spec_not_generate_spec
def test_flask_context_module_uses_get_docs_spec_not_generate_spec():
    '''
    Assert FlaskApiContext snapshots docs through get_docs_spec.
    '''

    # Read the Flask API context module source.
    source = inspect.getsource(flask_context_module)

    # Assert the module snapshots via get_docs_spec and does not use generate_spec.
    assert 'self.get_docs_spec(' in source
    assert 'generate_spec' not in source

# *** testers

# ** tester: test_flask_api_context
@use_tester(type='generic', target_cls=FlaskApiContext)
class TestFlaskApiContext:
    '''
    Tests for FlaskApiContext.
    '''

    # * test: get_routers_calls_handler_directly
    def test_get_routers_calls_handler_directly(
            self,
            session,
            flask_api_context: FlaskApiContext,
            get_routers_handler: Callable,
            sample_router: ApiRouter,
        ):
        '''
        Assert get_routers invokes the injected handler with no arguments.

        :param session: A fresh generic test session.
        :type session: TestSessionContext
        :param flask_api_context: The FlaskApiContext under test.
        :type flask_api_context: FlaskApiContext
        :param get_routers_handler: The injected routers handler mock.
        :type get_routers_handler: Callable
        :param sample_router: The sample router returned by the handler.
        :type sample_router: ApiRouter
        '''

        # Arrange the injected handler to return the sample router.
        get_routers_handler.return_value = [sample_router]

        # Exercise get_routers through the generic test session.
        result = session.run(target=flask_api_context.get_routers)

        # Assert the handler result is returned unchanged.
        assert result == [sample_router]

        # Assert the stored callable was invoked with no arguments.
        get_routers_handler.assert_called_once_with()

    # * test: create_swagger_blueprint_returns_docs_blueprint
    def test_create_swagger_blueprint_returns_docs_blueprint(
            self,
            session,
            flask_api_context: FlaskApiContext,
            get_routers_handler: Callable,
        ):
        '''
        Assert create_swagger_blueprint returns the vendored docs Blueprint.

        :param session: A fresh generic test session.
        :type session: TestSessionContext
        :param flask_api_context: The FlaskApiContext under test.
        :type flask_api_context: FlaskApiContext
        :param get_routers_handler: The injected routers handler mock.
        :type get_routers_handler: Callable
        '''

        # Arrange an empty router catalog for spec snapshotting.
        get_routers_handler.return_value = []

        # Exercise create_swagger_blueprint through the generic test session.
        result = session.given(title='Test API').run(
            target=flask_api_context.create_swagger_blueprint
        )

        # Assert the docs Blueprint is wired to vendored static assets.
        assert isinstance(result, Blueprint)
        assert result.name == SWAGGER_BLUEPRINT_NAME
        assert result.url_prefix == SWAGGER_URL_PREFIX
        assert len(result.deferred_functions) == 2
        assert result.has_static_folder is True
        assert result.static_folder == SWAGGER_STATIC_FOLDER

    # * test: create_swagger_blueprint_uses_get_docs_spec
    def test_create_swagger_blueprint_uses_get_docs_spec(
            self,
            session,
            flask_api_context: FlaskApiContext,
            get_routers_handler: Callable,
        ):
        '''
        Assert the first call snapshots the spec via get_docs_spec.

        :param session: A fresh generic test session.
        :type session: TestSessionContext
        :param flask_api_context: The FlaskApiContext under test.
        :type flask_api_context: FlaskApiContext
        :param get_routers_handler: The injected routers handler mock.
        :type get_routers_handler: Callable
        '''

        # Arrange an empty router catalog for spec snapshotting.
        get_routers_handler.return_value = []

        # Wrap get_docs_spec and exercise the first blueprint build.
        with mock.patch.object(
            flask_api_context,
            'get_docs_spec',
            wraps=flask_api_context.get_docs_spec,
        ) as get_docs_spec:
            session.given(
                title='Test API',
                version='2.0.0',
                description='desc',
            ).run(target=flask_api_context.create_swagger_blueprint)

        # Assert get_docs_spec received the first-call identity kwargs.
        get_docs_spec.assert_called_once_with(
            title='Test API',
            version='2.0.0',
            description='desc',
        )

    # * test: create_swagger_blueprint_second_call_is_cached_no_op
    def test_create_swagger_blueprint_second_call_is_cached_no_op(
            self,
            session,
            flask_api_context: FlaskApiContext,
            get_routers_handler: Callable,
        ):
        '''
        Assert a second call returns the cached Blueprint without a new snapshot.

        :param session: A fresh generic test session.
        :type session: TestSessionContext
        :param flask_api_context: The FlaskApiContext under test.
        :type flask_api_context: FlaskApiContext
        :param get_routers_handler: The injected routers handler mock.
        :type get_routers_handler: Callable
        '''

        # Arrange an empty router catalog for spec snapshotting.
        get_routers_handler.return_value = []

        # Wrap get_docs_spec around the first and second blueprint calls.
        with mock.patch.object(
            flask_api_context,
            'get_docs_spec',
            wraps=flask_api_context.get_docs_spec,
        ) as get_docs_spec:
            first = session.given(title='Test API').run(
                target=flask_api_context.create_swagger_blueprint
            )
            second = flask_api_context.create_swagger_blueprint(
                title='Different Title'
            )

        # Assert the cached Blueprint is returned without a second snapshot.
        assert second is first
        get_docs_spec.assert_called_once()

    # * test: swagger_ui_serves_vendored_assets_without_cdn
    def test_swagger_ui_serves_vendored_assets_without_cdn(
            self,
            session,
            flask_api_context: FlaskApiContext,
            get_routers_handler: Callable,
        ):
        '''
        Assert the docs UI serves vendored CSS/JS with no CDN hosts.

        :param session: A fresh generic test session.
        :type session: TestSessionContext
        :param flask_api_context: The FlaskApiContext under test.
        :type flask_api_context: FlaskApiContext
        :param get_routers_handler: The injected routers handler mock.
        :type get_routers_handler: Callable
        '''

        # Arrange an empty router catalog and register the swagger Blueprint.
        get_routers_handler.return_value = []
        swagger_bp = session.given(title='Test API').run(
            target=flask_api_context.create_swagger_blueprint
        )
        app = Flask(__name__)
        app.register_blueprint(swagger_bp)
        client = app.test_client()

        # Assert the UI HTML has no CDN hosts.
        response = client.get(f'{SWAGGER_URL_PREFIX}/')
        assert response.status_code == 200
        text = response.get_data(as_text=True)
        assert 'jsdelivr' not in text
        assert 'cdn.jsdelivr.net' not in text

        # Assert vendored CSS and JS bytes are served unchanged.
        css_response = client.get(
            f'{SWAGGER_URL_PREFIX}{SWAGGER_STATIC_URL_PATH}/{SWAGGER_UI_CSS_FILENAME}'
        )
        js_response = client.get(
            f'{SWAGGER_URL_PREFIX}{SWAGGER_STATIC_URL_PATH}/{SWAGGER_UI_BUNDLE_JS_FILENAME}'
        )
        assert css_response.status_code == 200
        assert js_response.status_code == 200
        assert css_response.get_data() == (
            Path(SWAGGER_STATIC_FOLDER) / SWAGGER_UI_CSS_FILENAME
        ).read_bytes()
        assert js_response.get_data() == (
            Path(SWAGGER_STATIC_FOLDER) / SWAGGER_UI_BUNDLE_JS_FILENAME
        ).read_bytes()

    # * test: docs_openapi_json_returns_spec_snapshot
    def test_docs_openapi_json_returns_spec_snapshot(
            self,
            session,
            flask_api_context: FlaskApiContext,
            get_routers_handler: Callable,
        ):
        '''
        Assert /docs/openapi.json returns the first-call spec snapshot.

        :param session: A fresh generic test session.
        :type session: TestSessionContext
        :param flask_api_context: The FlaskApiContext under test.
        :type flask_api_context: FlaskApiContext
        :param get_routers_handler: The injected routers handler mock.
        :type get_routers_handler: Callable
        '''

        # Arrange an empty router catalog and register the swagger Blueprint.
        get_routers_handler.return_value = []
        swagger_bp = session.given(title='Snapshot API').run(
            target=flask_api_context.create_swagger_blueprint
        )
        app = Flask(__name__)
        app.register_blueprint(swagger_bp)
        client = app.test_client()

        # Assert the snapshot title is served from /docs/openapi.json.
        response = client.get(SWAGGER_OPENAPI_JSON_PATH)
        assert response.status_code == 200
        assert response.get_json()['info']['title'] == 'Snapshot API'
