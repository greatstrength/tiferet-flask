# *** imports

# ** infra
import pytest
from unittest import mock
from flask import Blueprint
from tiferet.events import DomainEvent
from tiferet.di import ServiceProvider
from tiferet_openapi import ApiRoute, ApiRouter

# ** app
from ..flask import get_routers, build_blueprint


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

    return mock.Mock()


# ** fixture: mock_service_provider
@pytest.fixture
def mock_service_provider(sample_router: ApiRouter) -> mock.Mock:
    '''
    Fixture to provide a mock ServiceProvider with get_routers_evt.
    '''

    # Create a mock get_routers event.
    mock_get_routers_evt = mock.Mock(spec=DomainEvent)
    mock_get_routers_evt.execute = mock.Mock(return_value=[sample_router])

    # Create the mock service provider.
    provider = mock.Mock(spec=ServiceProvider)
    provider.get_service = mock.Mock(return_value=mock_get_routers_evt)

    return provider


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


# ** test: get_routers
def test_get_routers(mock_service_provider: mock.Mock, sample_router: ApiRouter):
    '''
    Test get_routers resolves and executes the get_routers event.
    '''

    # Get the routers.
    routers = get_routers(mock_service_provider)

    # Assert the service provider was called correctly.
    mock_service_provider.get_service.assert_called_once_with('get_routers_evt')

    # Assert the result contains the expected router.
    assert len(routers) == 1
    assert routers[0] is sample_router
