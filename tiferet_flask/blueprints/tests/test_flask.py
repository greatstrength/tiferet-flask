# *** imports

# ** infra
import pytest
from unittest import mock
from flask import Flask, Blueprint
from tiferet.events import DomainEvent
from tiferet_openapi import ApiRoute, ApiRouter

# ** app
from ..flask import get_routers, build_blueprint, build_flask_app


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


# ** fixture: mock_interface_context
@pytest.fixture
def mock_interface_context(sample_router: ApiRouter) -> mock.Mock:
    '''
    Fixture to provide a mock interface context with a get_routers_handler.
    '''

    # Create the mock interface context.
    context = mock.Mock()
    context.get_routers_handler = mock.Mock(return_value=[sample_router])

    return context


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
def test_get_routers(mock_interface_context: mock.Mock, sample_router: ApiRouter):
    '''
    Test get_routers executes the get_routers_handler on the interface context.
    '''

    # Get the routers.
    routers = get_routers(mock_interface_context)

    # Assert the handler was called.
    mock_interface_context.get_routers_handler.assert_called_once()

    # Assert the result contains the expected router.
    assert len(routers) == 1
    assert routers[0] is sample_router


# ** test: get_routers_empty
def test_get_routers_empty():
    '''
    Test get_routers returns an empty list when no routers are configured.
    '''

    # Create a context with no routers.
    context = mock.Mock()
    context.get_routers_handler = mock.Mock(return_value=[])

    # Get the routers.
    routers = get_routers(context)

    # Assert the result is empty.
    assert routers == []


# ** test: build_flask_app_registers_blueprints
def test_build_flask_app_registers_blueprints(sample_router: ApiRouter, mock_view_func: mock.Mock):
    '''
    Test build_flask_app creates a Flask app with registered blueprints.
    '''

    # Mock resolve_interface and realize_interface.
    mock_app_interface = mock.Mock()
    mock_context = mock.Mock()
    mock_context.get_routers_handler = mock.Mock(return_value=[sample_router])

    with mock.patch('tiferet_flask.blueprints.flask.resolve_interface', return_value=(mock_app_interface, [])) as mock_resolve, \
         mock.patch('tiferet_flask.blueprints.flask.realize_interface', return_value=mock_context) as mock_realize:

        # Build the Flask app.
        flask_app = build_flask_app('test_interface', mock_view_func, app_yaml_file='app.yml')

    # Assert a Flask app was returned.
    assert isinstance(flask_app, Flask)

    # Assert resolve_interface was called with correct params.
    mock_resolve.assert_called_once_with('test_interface', app_yaml_file='app.yml')

    # Assert realize_interface was called with the resolved interface.
    mock_realize.assert_called_once_with(mock_app_interface, 'test_interface')

    # Assert routers were loaded from the context.
    mock_context.get_routers_handler.assert_called_once()


# ** test: build_flask_app_with_swagger
def test_build_flask_app_with_swagger(mock_view_func: mock.Mock):
    '''
    Test build_flask_app registers a Swagger blueprint when swagger=True.
    '''

    # Mock resolve_interface and realize_interface.
    mock_app_interface = mock.Mock()
    mock_swagger_bp = Blueprint('swagger', __name__, url_prefix='/docs')
    mock_context = mock.Mock()
    mock_context.get_routers_handler = mock.Mock(return_value=[])
    mock_context.create_swagger_blueprint = mock.Mock(return_value=mock_swagger_bp)

    with mock.patch('tiferet_flask.blueprints.flask.resolve_interface', return_value=(mock_app_interface, [])), \
         mock.patch('tiferet_flask.blueprints.flask.realize_interface', return_value=mock_context):

        # Build the Flask app with swagger enabled.
        flask_app = build_flask_app('test_interface', mock_view_func, swagger=True, app_yaml_file='app.yml')

    # Assert create_swagger_blueprint was called.
    mock_context.create_swagger_blueprint.assert_called_once()

    # Assert the swagger blueprint was registered.
    assert 'swagger' in flask_app.blueprints


# ** test: build_flask_app_without_swagger
def test_build_flask_app_without_swagger(mock_view_func: mock.Mock):
    '''
    Test build_flask_app does not register Swagger when swagger=False.
    '''

    # Mock resolve_interface and realize_interface.
    mock_app_interface = mock.Mock()
    mock_context = mock.Mock()
    mock_context.get_routers_handler = mock.Mock(return_value=[])
    mock_context.create_swagger_blueprint = mock.Mock()

    with mock.patch('tiferet_flask.blueprints.flask.resolve_interface', return_value=(mock_app_interface, [])), \
         mock.patch('tiferet_flask.blueprints.flask.realize_interface', return_value=mock_context):

        # Build the Flask app without swagger.
        flask_app = build_flask_app('test_interface', mock_view_func, swagger=False, app_yaml_file='app.yml')

    # Assert create_swagger_blueprint was NOT called.
    mock_context.create_swagger_blueprint.assert_not_called()

    # Assert no swagger blueprint was registered.
    assert 'swagger' not in flask_app.blueprints


# ** test: build_flask_app_does_not_leak_params_to_swagger
def test_build_flask_app_does_not_leak_params_to_swagger(mock_view_func: mock.Mock):
    '''
    Test build_flask_app does not pass resolve_interface params to create_swagger_blueprint.
    '''

    # Mock resolve_interface and realize_interface.
    mock_app_interface = mock.Mock()
    mock_swagger_bp = Blueprint('swagger', __name__, url_prefix='/docs')
    mock_context = mock.Mock()
    mock_context.get_routers_handler = mock.Mock(return_value=[])
    mock_context.create_swagger_blueprint = mock.Mock(return_value=mock_swagger_bp)

    with mock.patch('tiferet_flask.blueprints.flask.resolve_interface', return_value=(mock_app_interface, [])), \
         mock.patch('tiferet_flask.blueprints.flask.realize_interface', return_value=mock_context):

        # Build the Flask app with extra parameters.
        flask_app = build_flask_app(
            'test_interface', mock_view_func,
            swagger=True,
            app_yaml_file='app.yml',
            extra_param='should_not_leak',
        )

    # Assert create_swagger_blueprint was called with no arguments.
    mock_context.create_swagger_blueprint.assert_called_once_with()
