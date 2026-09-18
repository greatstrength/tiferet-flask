# *** imports

# ** core
import inspect
from pathlib import Path
from typing import Callable
from unittest import mock

# ** infra
import pytest
from flask import Flask, Blueprint
from tiferet import use_tester
from tiferet.contexts.app import AppSessionContext
from tiferet.contexts.core import BaseContext, ContextMeta
from tiferet.domain import AppSession
from tiferet_openapi import ApiRoute, ApiRouter

# ** app
from .. import flask as flask_context_module
from ..flask import SWAGGER_STATIC_FOLDER, FlaskApiContext

# *** fixtures

# ** fixture: app_session
@pytest.fixture
def app_session() -> AppSession:
    '''
    Fixture to provide the AppSession bound to the FlaskApiContext under test.
    '''

    return AppSession(id='test_flask', name='Test Flask API')

# ** fixture: get_dependency
@pytest.fixture
def get_dependency() -> Callable:
    '''
    Fixture to provide a mock DI resolution handler.
    '''

    return mock.Mock()

# ** fixture: get_route_handler
@pytest.fixture
def get_route_handler() -> Callable:
    '''
    Fixture to provide a mock route-lookup handler.
    '''

    return mock.Mock()

# ** fixture: get_status_code_handler
@pytest.fixture
def get_status_code_handler() -> Callable:
    '''
    Fixture to provide a mock status-code-lookup handler.
    '''

    return mock.Mock()

# ** fixture: get_routers_handler
@pytest.fixture
def get_routers_handler() -> Callable:
    '''
    Fixture to provide a mock routers-lookup handler.
    '''

    return mock.Mock()

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
    Fixture to provide a FlaskApiContext bound via from_domain, mirroring the
    cut tiferet-openapi==1.0.0 OpenApiSessionContext constructor shape.
    '''

    return FlaskApiContext.from_domain(
        app_session,
        get_dependency=get_dependency,
        get_route_handler=get_route_handler,
        get_status_code_handler=get_status_code_handler,
        get_routers_handler=get_routers_handler,
    )

# ** fixture: sample_router
@pytest.fixture
def sample_router() -> ApiRouter:
    '''
    Fixture to provide a sample ApiRouter with one route.
    '''

    return ApiRouter(
        name='calc',
        prefix='/calc',
        routes=[
            ApiRoute(id='add', endpoint='calc.add', path='/add', methods=['POST'], status_code=200),
        ],
    )

# *** tests

# ** test: flask_api_context_not_registered
def test_flask_api_context_not_registered():
    '''
    Verify FlaskApiContext declares no domain_type, does not steal the
    AppSession registry slot from AppSessionContext, and drops the retired
    create_docs_handler override (RFP-001 item 3).
    '''

    # Verify domain_type is not declared in FlaskApiContext's own namespace.
    assert 'domain_type' not in FlaskApiContext.__dict__

    # Verify FlaskApiContext never registered itself in the context registry.
    assert FlaskApiContext not in ContextMeta.registry.values()

    # Verify AppSession still resolves to the base application session hub.
    assert BaseContext.for_domain(AppSession) is AppSessionContext

    # Verify the retired create_docs_handler override is absent.
    assert 'create_docs_handler' not in FlaskApiContext.__dict__

# ** test: flask_context_module_uses_get_docs_spec_not_generate_spec
def test_flask_context_module_uses_get_docs_spec_not_generate_spec():
    '''
    Verify tiferet_flask/contexts/flask.py wraps get_docs_spec and never
    references generate_spec (RFP-003 item 1 / AC).
    '''

    # Read the module source once.
    source = inspect.getsource(flask_context_module)

    # Verify get_docs_spec is the wrapped Publish accessor.
    assert 'self.get_docs_spec(' in source

    # Verify generate_spec is never referenced from this module.
    assert 'generate_spec' not in source

# *** testers

# ** tester: test_flask_api_context
@use_tester(
    type='generic',
    target_cls=FlaskApiContext,
)
class TestFlaskApiContext:
    '''
    Generic tester covering the RFP-001 methods FlaskApiContext adds on top
    of OpenApiSessionContext: get_routers and create_swagger_blueprint.
    '''

    # * test: get_routers_calls_handler_directly
    def test_get_routers_calls_handler_directly(
            self,
            session,
            flask_api_context: FlaskApiContext,
            get_routers_handler: Callable,
            sample_router: ApiRouter,
        ) -> None:
        '''
        Verify get_routers returns whatever the injected get_routers_handler
        mock returns when _get_routers() is called directly, not .execute().
        '''

        # Configure the injected handler to return a known router list.
        get_routers_handler.return_value = [sample_router]

        # Exercise get_routers as a bound-method target.
        result = session.run(target=flask_api_context.get_routers)

        # Assert the result and the direct call shape.
        assert result == [sample_router]
        get_routers_handler.assert_called_once_with()

    # * test: create_swagger_blueprint_returns_docs_blueprint
    def test_create_swagger_blueprint_returns_docs_blueprint(
            self,
            session,
            flask_api_context: FlaskApiContext,
            get_routers_handler: Callable,
        ) -> None:
        '''
        Verify create_swagger_blueprint returns a Flask Blueprint named
        swagger with the /docs prefix, wired to the vendored static folder
        (RFP-003).
        '''

        # Configure no routers so get_docs_spec has an empty paths dict.
        get_routers_handler.return_value = []

        # Exercise create_swagger_blueprint as a bound-method target.
        result = session.given(title='Test API').run(target=flask_api_context.create_swagger_blueprint)

        # Assert the Blueprint shape.
        assert isinstance(result, Blueprint)
        assert result.name == 'swagger'
        assert result.url_prefix == '/docs'
        assert len(result.deferred_functions) == 2
        assert result.has_static_folder
        assert result.static_folder == SWAGGER_STATIC_FOLDER

    # * test: create_swagger_blueprint_uses_get_docs_spec
    def test_create_swagger_blueprint_uses_get_docs_spec(
            self,
            session,
            flask_api_context: FlaskApiContext,
            get_routers_handler: Callable,
        ) -> None:
        '''
        Verify create_swagger_blueprint calls get_docs_spec with the given
        title/version/description (RFP-003 item 1).
        '''

        # Configure no routers.
        get_routers_handler.return_value = []

        # Wrap get_docs_spec to observe the call while preserving behavior.
        with mock.patch.object(
                flask_api_context,
                'get_docs_spec',
                wraps=flask_api_context.get_docs_spec,
            ) as mock_get_docs_spec:

            # Exercise create_swagger_blueprint as a bound-method target.
            session.given(title='Test API', version='2.0.0', description='desc').run(
                target=flask_api_context.create_swagger_blueprint,
            )

        # Assert get_docs_spec was called with the given kwargs.
        mock_get_docs_spec.assert_called_once_with(title='Test API', version='2.0.0', description='desc')

    # * test: create_swagger_blueprint_second_call_is_cached_no_op
    def test_create_swagger_blueprint_second_call_is_cached_no_op(
            self,
            session,
            flask_api_context: FlaskApiContext,
            get_routers_handler: Callable,
        ) -> None:
        '''
        Verify a second create_swagger_blueprint call returns the cached
        Blueprint and does not call get_docs_spec again (RFP-003 item 3).
        '''

        # Configure no routers.
        get_routers_handler.return_value = []

        # Wrap get_docs_spec to count invocations across both calls.
        with mock.patch.object(
                flask_api_context,
                'get_docs_spec',
                wraps=flask_api_context.get_docs_spec,
            ) as mock_get_docs_spec:

            # Exercise the first call as a bound-method target.
            first = session.given(title='Test API').run(target=flask_api_context.create_swagger_blueprint)

            # Exercise a second call directly, with different kwargs.
            second = flask_api_context.create_swagger_blueprint(title='Different Title')

        # Assert the cached object is returned and get_docs_spec ran once.
        assert second is first
        mock_get_docs_spec.assert_called_once()

    # * test: swagger_ui_serves_vendored_assets_without_cdn
    def test_swagger_ui_serves_vendored_assets_without_cdn(
            self,
            session,
            flask_api_context: FlaskApiContext,
            get_routers_handler: Callable,
        ) -> None:
        '''
        Verify /docs/ HTML has no CDN hosts and /docs/assets/* serves the
        vendored swagger-ui-dist bytes with HTTP 200 (RFP-003 items 5-6).
        '''

        # Configure no routers.
        get_routers_handler.return_value = []

        # Build the swagger blueprint and register it on a throwaway app.
        swagger_bp = session.given(title='Test API').run(target=flask_api_context.create_swagger_blueprint)
        app = Flask(__name__)
        app.register_blueprint(swagger_bp)
        client = app.test_client()

        # Assert the docs page has no CDN references.
        docs_response = client.get('/docs/')
        html = docs_response.get_data(as_text=True)
        assert docs_response.status_code == 200
        assert 'jsdelivr' not in html
        assert 'cdn.jsdelivr.net' not in html

        # Assert the vendored assets are served with the exact vendored bytes.
        css_response = client.get('/docs/assets/swagger-ui.css')
        bundle_response = client.get('/docs/assets/swagger-ui-bundle.js')
        assert css_response.status_code == 200
        assert bundle_response.status_code == 200
        assert css_response.data == (Path(SWAGGER_STATIC_FOLDER) / 'swagger-ui.css').read_bytes()
        assert bundle_response.data == (Path(SWAGGER_STATIC_FOLDER) / 'swagger-ui-bundle.js').read_bytes()

    # * test: docs_openapi_json_returns_spec_snapshot
    def test_docs_openapi_json_returns_spec_snapshot(
            self,
            session,
            flask_api_context: FlaskApiContext,
            get_routers_handler: Callable,
        ) -> None:
        '''
        Verify /docs/openapi.json returns the spec snapshot taken at build
        time by get_docs_spec (RFP-003 item 1).
        '''

        # Configure no routers.
        get_routers_handler.return_value = []

        # Build the swagger blueprint and register it on a throwaway app.
        swagger_bp = session.given(title='Snapshot API').run(target=flask_api_context.create_swagger_blueprint)
        app = Flask(__name__)
        app.register_blueprint(swagger_bp)
        client = app.test_client()

        # Assert the snapshot spec is served as JSON.
        response = client.get('/docs/openapi.json')
        assert response.status_code == 200
        assert response.get_json()['info']['title'] == 'Snapshot API'
