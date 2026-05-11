# *** imports

# ** infra
import pytest
from unittest import mock
from flask import Blueprint
from tiferet.assets.exceptions import TiferetAPIError
from tiferet.contexts.error import ErrorContext
from tiferet.contexts.feature import FeatureContext
from tiferet.contexts.logging import LoggingContext
from tiferet import TiferetError
from tiferet.events import DomainEvent
from tiferet_openapi import ApiRoute, ApiRouter

# ** app
from ..flask import FlaskApiContext
from ..request import FlaskRequestContext

# *** fixtures

# ** fixture: sample_route
@pytest.fixture
def sample_route() -> ApiRoute:
    '''
    Fixture to provide a sample ApiRoute.
    '''

    return ApiRoute(
        id='sample_route',
        endpoint='sample_router.sample_route',
        path='/sample',
        methods=['GET', 'POST'],
        status_code=269,
    )

# ** fixture: flask_api_context
@pytest.fixture
def flask_api_context(sample_route: ApiRoute) -> FlaskApiContext:
    '''
    Fixture to provide a FlaskApiContext instance for testing.
    '''

    # Create mock contexts.
    mock_features = mock.Mock(spec=FeatureContext)
    mock_errors = mock.Mock(spec=ErrorContext)
    mock_errors.handle_error.return_value = {'error_code': 'APP_ERROR', 'name': 'Application Error', 'message': 'An error occurred.'}
    mock_logging = mock.Mock(spec=LoggingContext)

    # Create mock DomainEvent instances.
    mock_get_route_evt = mock.Mock(spec=DomainEvent)
    mock_get_route_evt.execute = mock.Mock(return_value=sample_route)
    mock_get_status_code_evt = mock.Mock(spec=DomainEvent)
    mock_get_status_code_evt.execute = mock.Mock(return_value=420)
    mock_get_routers_evt = mock.Mock(spec=DomainEvent)
    mock_get_routers_evt.execute = mock.Mock(return_value=[])

    # Create and return the FlaskApiContext instance.
    return FlaskApiContext(
        interface_id='test_flask',
        features=mock_features,
        errors=mock_errors,
        logging=mock_logging,
        get_route_evt=mock_get_route_evt,
        get_status_code_evt=mock_get_status_code_evt,
        get_routers_evt=mock_get_routers_evt,
    )

# *** tests

# ** test: flask_api_parse_request
def test_flask_api_parse_request(flask_api_context: FlaskApiContext):
    '''
    Test the parse_request method of FlaskApiContext.
    '''

    # Sample headers and data.
    sample_headers = {'Content-Type': 'application/json'}
    sample_data = {'key': 'value'}

    # Parse the request.
    request_context = flask_api_context.parse_request(
        headers=sample_headers,
        data=sample_data,
        feature_id='test_feature',
    )

    # Assert that the returned object is a FlaskRequestContext instance.
    assert isinstance(request_context, FlaskRequestContext)
    assert request_context.headers == sample_headers
    assert request_context.data == sample_data
    assert request_context.feature_id == 'test_feature'

# ** test: flask_api_context_handle_error
def test_flask_api_context_handle_error(flask_api_context: FlaskApiContext):
    '''
    Test the handle_error method with a non-TiferetError exception.
    '''

    # Create a sample exception.
    sample_exception = Exception('Sample error')

    # Handle the error and expect TiferetAPIError.
    with pytest.raises(TiferetAPIError) as exc_info:
        flask_api_context.handle_error(sample_exception)

    # Assert the status code is 500 for generic errors.
    assert exc_info.value.status_code == 500

# ** test: flask_api_context_handle_tiferet_error
def test_flask_api_context_handle_tiferet_error(flask_api_context: FlaskApiContext):
    '''
    Test the handle_error method with a TiferetError.
    '''

    # Create a sample TiferetError.
    sample_tiferet_error = TiferetError('TEST_ERROR', 'A test Tiferet error occurred.')

    # Handle the error and expect TiferetAPIError.
    with pytest.raises(TiferetAPIError) as exc_info:
        flask_api_context.handle_error(sample_tiferet_error)

    # Assert the status code from the handler.
    assert exc_info.value.status_code == 420

    # Assert the handler was called with the correct error code.
    flask_api_context.get_status_code_handler.assert_called_once_with(
        error_code='TEST_ERROR'
    )

# ** test: flask_api_context_handle_response
def test_flask_api_context_handle_response(flask_api_context: FlaskApiContext):
    '''
    Test the handle_response method.
    '''

    # Create a new request context.
    request_context = flask_api_context.parse_request(
        headers={'Content-Type': 'application/json'},
        data={'key': 'value'},
        feature_id='test_feature',
    )

    # Set a sample result in the request context.
    request_context.set_result({'result_key': 'result_value'})

    # Handle the response.
    response, status_code = flask_api_context.handle_response(request_context)

    # Assert the response and status code.
    assert response == {'result_key': 'result_value'}
    assert status_code == 269

    # Assert the route handler was called with the feature id.
    flask_api_context.get_route_handler.assert_called_once_with(
        endpoint='test_feature'
    )

# ** test: flask_api_context_generate_spec_single_router
def test_flask_api_context_generate_spec_single_router(flask_api_context: FlaskApiContext):
    '''
    Test generate_spec with a single router containing multiple routes.
    '''

    # Set up the routers mock to return a single router.
    sample_router = ApiRouter(
        name='calc',
        prefix='/calc',
        routes=[
            ApiRoute(id='add', endpoint='calc.add', path='/add', methods=['POST'], status_code=200),
            ApiRoute(id='subtract', endpoint='calc.subtract', path='/subtract', methods=['POST'], status_code=200),
        ],
    )
    flask_api_context.get_routers_handler = mock.Mock(return_value=[sample_router])

    # Generate the spec.
    spec = flask_api_context.generate_spec(title='Calc API', version='2.0.0', description='A calculator')

    # Assert the spec structure.
    assert spec['openapi'] == '3.0.3'
    assert spec['info']['title'] == 'Calc API'
    assert spec['info']['version'] == '2.0.0'
    assert spec['info']['description'] == 'A calculator'
    assert '/calc/add' in spec['paths']
    assert '/calc/subtract' in spec['paths']
    assert spec['paths']['/calc/add']['post']['operationId'] == 'calc.add'

# ** test: flask_api_context_generate_spec_multi_router
def test_flask_api_context_generate_spec_multi_router(flask_api_context: FlaskApiContext):
    '''
    Test generate_spec with multiple routers.
    '''

    # Set up the routers mock to return two routers.
    routers = [
        ApiRouter(
            name='calc',
            prefix='/calc',
            routes=[ApiRoute(id='add', endpoint='calc.add', path='/add', methods=['POST'], status_code=200)],
        ),
        ApiRouter(
            name='health',
            prefix=None,
            routes=[ApiRoute(id='ping', endpoint='health.ping', path='/ping', methods=['GET'], status_code=200)],
        ),
    ]
    flask_api_context.get_routers_handler = mock.Mock(return_value=routers)

    # Generate the spec.
    spec = flask_api_context.generate_spec()

    # Assert paths from both routers are present.
    assert '/calc/add' in spec['paths']
    assert '/ping' in spec['paths']
    assert spec['info']['title'] == 'API'

# ** test: flask_api_context_create_swagger_blueprint
def test_flask_api_context_create_swagger_blueprint(flask_api_context: FlaskApiContext):
    '''
    Test create_swagger_blueprint returns a Flask Blueprint with correct routes.
    '''

    # Set up routers mock.
    flask_api_context.get_routers_handler = mock.Mock(return_value=[])

    # Create the swagger blueprint.
    swagger_bp = flask_api_context.create_swagger_blueprint(title='Test API')

    # Assert it is a Blueprint with the expected name and prefix.
    assert isinstance(swagger_bp, Blueprint)
    assert swagger_bp.name == 'swagger'
    assert swagger_bp.url_prefix == '/docs'

    # Assert the blueprint has the expected deferred view functions.
    rules = [rule for rule in swagger_bp.deferred_functions]
    assert len(rules) == 2  # openapi_json and swagger_ui

# ** test: flask_api_context_create_docs_handler
def test_flask_api_context_create_docs_handler(flask_api_context: FlaskApiContext):
    '''
    Test create_docs_handler delegates to create_swagger_blueprint.
    '''

    # Set up routers mock.
    flask_api_context.get_routers_handler = mock.Mock(return_value=[])

    # Call create_docs_handler.
    result = flask_api_context.create_docs_handler(title='Docs API')

    # Assert it returns a Blueprint.
    assert isinstance(result, Blueprint)
    assert result.name == 'swagger'
