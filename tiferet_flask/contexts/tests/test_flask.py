# *** imports

# ** core
from typing import Callable
from unittest import mock

# ** infra
import pytest
from tiferet import use_tester
from tiferet.contexts.app import AppSessionContext
from tiferet.contexts.core import BaseContext, ContextMeta
from tiferet.domain import AppSession
from tiferet_openapi import ApiRoute, ApiRouter

# ** app
from ..flask import FlaskApiContext

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
