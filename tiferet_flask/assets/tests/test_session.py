# *** imports

# ** core
from unittest import mock

# ** infra
from tiferet import use_tester

# ** app
from ..session import (
    APP_FLAG,
    GET_ROUTE_EVT_SERVICE_ID,
    GET_ROUTERS_EVT_SERVICE_ID,
    GET_STATUS_CODE_EVT_SERVICE_ID,
    get_route_handler,
    get_routers_handler,
    get_status_code_handler,
)

# *** testers

# ** tester: test_get_route_handler
@use_tester(
    type='generic',
    target_cls=get_route_handler,
)
class TestGetRouteHandler:
    '''
    Generic tester for get_route_handler.
    '''

    # * test: resolves_service_id_and_app_flag
    def test_get_route_handler_resolves_service_id_and_app_flag(self, session) -> None:
        '''
        Verify the built closure resolves the get-route event with the
        service id and 'app' flag, then calls execute(**kwargs).
        '''

        # Build a mock get_dependency resolver returning a mock event.
        get_route_evt = mock.Mock()
        get_route_evt.execute = mock.Mock(return_value=mock.sentinel.route)
        get_dependency = mock.Mock(return_value=get_route_evt)

        # Exercise get_route_handler to build the closure, then call it.
        handler = session.given(get_dependency=get_dependency).run(target=get_route_handler)
        result = handler(id='calc.add')

        # Assert the resolution shape and passthrough return value.
        get_dependency.assert_called_once_with(GET_ROUTE_EVT_SERVICE_ID, APP_FLAG)
        get_route_evt.execute.assert_called_once_with(id='calc.add')
        assert result is mock.sentinel.route

# ** tester: test_get_status_code_handler
@use_tester(
    type='generic',
    target_cls=get_status_code_handler,
)
class TestGetStatusCodeHandler:
    '''
    Generic tester for get_status_code_handler.
    '''

    # * test: resolves_service_id_and_app_flag
    def test_get_status_code_handler_resolves_service_id_and_app_flag(self, session) -> None:
        '''
        Verify the built closure resolves the get-status-code event with the
        service id and 'app' flag, then calls execute(**kwargs).
        '''

        # Build a mock get_dependency resolver returning a mock event.
        get_status_code_evt = mock.Mock()
        get_status_code_evt.execute = mock.Mock(return_value=mock.sentinel.status_code)
        get_dependency = mock.Mock(return_value=get_status_code_evt)

        # Exercise get_status_code_handler to build the closure, then call it.
        handler = session.given(get_dependency=get_dependency).run(target=get_status_code_handler)
        result = handler(error_code='DIVISION_BY_ZERO')

        # Assert the resolution shape and passthrough return value.
        get_dependency.assert_called_once_with(GET_STATUS_CODE_EVT_SERVICE_ID, APP_FLAG)
        get_status_code_evt.execute.assert_called_once_with(error_code='DIVISION_BY_ZERO')
        assert result is mock.sentinel.status_code

# ** tester: test_get_routers_handler
@use_tester(
    type='generic',
    target_cls=get_routers_handler,
)
class TestGetRoutersHandler:
    '''
    Generic tester for get_routers_handler.
    '''

    # * test: resolves_service_id_and_app_flag
    def test_get_routers_handler_resolves_service_id_and_app_flag(self, session) -> None:
        '''
        Verify the built closure resolves the get-routers event with the
        service id and 'app' flag, then calls execute(**kwargs).
        '''

        # Build a mock get_dependency resolver returning a mock event.
        get_routers_evt = mock.Mock()
        get_routers_evt.execute = mock.Mock(return_value=mock.sentinel.routers)
        get_dependency = mock.Mock(return_value=get_routers_evt)

        # Exercise get_routers_handler to build the closure, then call it.
        handler = session.given(get_dependency=get_dependency).run(target=get_routers_handler)
        result = handler()

        # Assert the resolution shape and passthrough return value.
        get_dependency.assert_called_once_with(GET_ROUTERS_EVT_SERVICE_ID, APP_FLAG)
        get_routers_evt.execute.assert_called_once_with()
        assert result is mock.sentinel.routers
