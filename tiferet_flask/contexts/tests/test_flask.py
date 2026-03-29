# *** imports

# ** infra
import pytest
from unittest import mock
from flask import Flask, Blueprint
from tiferet import DomainObject
from tiferet.contexts.error import ErrorContext
from tiferet.contexts.feature import FeatureContext
from tiferet.contexts.logging import LoggingContext
from tiferet import TiferetError

# ** app
from ..flask import FlaskApiContext
from ..request import FlaskRequestContext
from ...domain import (
    FlaskBlueprint,
    FlaskRoute
)
from ...mappers import (
    FlaskBlueprintAggregate,
    FlaskRouteAggregate
)

# *** fixtures

# ** fixture: sample_route_aggregate
@pytest.fixture
def sample_route_aggregate() -> FlaskRouteAggregate:
    '''
    Fixture to provide a sample FlaskRouteAggregate.
    '''

    return FlaskRouteAggregate.new(
        id='sample_route',
        rule='/sample',
        methods=['GET', 'POST'],
        status_code=269
    )

# ** fixture: sample_blueprint_aggregate
@pytest.fixture
def sample_blueprint_aggregate(sample_route_aggregate: FlaskRouteAggregate) -> FlaskBlueprintAggregate:
    '''
    Fixture to provide a sample FlaskBlueprintAggregate.
    '''

    return FlaskBlueprintAggregate.new(
        name='sample_blueprint',
        routes=[sample_route_aggregate]
    )

# ** fixture: flask_api_context
@pytest.fixture
def flask_api_context(
    sample_blueprint_aggregate: FlaskBlueprintAggregate,
    sample_route_aggregate: FlaskRouteAggregate
) -> FlaskApiContext:
    '''
    Fixture to provide a FlaskApiContext instance for testing.
    '''

    # Create mock contexts.
    mock_features = mock.Mock(spec=FeatureContext)
    mock_errors = mock.Mock(spec=ErrorContext)
    mock_errors.handle_error.return_value = {'error_code': 'APP_ERROR', 'name': 'Application Error', 'message': 'An error occurred.'}
    mock_logging = mock.Mock(spec=LoggingContext)

    # Create mock callable handlers.
    mock_get_blueprints = mock.Mock(return_value=[sample_blueprint_aggregate])
    mock_get_route = mock.Mock(return_value=sample_route_aggregate)
    mock_get_status_code = mock.Mock(return_value=420)

    # Create and return the FlaskApiContext instance.
    return FlaskApiContext(
        interface_id='test_flask',
        features=mock_features,
        errors=mock_errors,
        logging=mock_logging,
        get_blueprints_handler=mock_get_blueprints,
        get_route_handler=mock_get_route,
        get_status_code_handler=mock_get_status_code,
    )

# *** tests

# ** test: flask_api_parse_request
def test_flask_api_parse_request(flask_api_context: FlaskApiContext):
    '''
    Test the parse_request method of FlaskApiContext.

    :param flask_api_context: A FlaskApiContext instance.
    :type flask_api_context: FlaskApiContext
    '''

    # Sample headers and data.
    sample_headers = {'Content-Type': 'application/json'}
    sample_data = {'key': 'value'}

    # Parse the request.
    request_context = flask_api_context.parse_request(
        headers=sample_headers,
        data=sample_data,
        feature_id='test_feature'
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

    :param flask_api_context: A FlaskApiContext instance.
    :type flask_api_context: FlaskApiContext
    '''

    # Create a sample exception.
    sample_exception = Exception('Sample error')

    # Handle the error.
    response, status_code = flask_api_context.handle_error(sample_exception)

    # Assert that the status code is 500 for generic errors.
    assert isinstance(response, dict)
    assert response['error_code'] == 'APP_ERROR'
    assert status_code == 500

# ** test: flask_api_context_handle_tiferet_error
def test_flask_api_context_handle_tiferet_error(flask_api_context: FlaskApiContext):
    '''
    Test the handle_error method with a TiferetError.

    :param flask_api_context: A FlaskApiContext instance.
    :type flask_api_context: FlaskApiContext
    '''

    # Create a sample TiferetError.
    sample_tiferet_error = TiferetError('TEST_ERROR', 'A test Tiferet error occurred.')

    # Mock the error handler to return a specific response.
    flask_api_context.errors.handle_error.return_value = {
        'error_code': 'TEST_ERROR',
        'name': 'Test Error',
        'message': 'A test Tiferet error occurred.'
    }

    # Call the handle_error method.
    response, status_code = flask_api_context.handle_error(sample_tiferet_error)

    # Assert the response and status code.
    assert response == {
        'error_code': 'TEST_ERROR',
        'name': 'Test Error',
        'message': 'A test Tiferet error occurred.'
    }
    assert status_code == 420

    # Assert the handler was called with the correct error code.
    flask_api_context.get_status_code_handler.assert_called_once_with(
        error_code='TEST_ERROR'
    )

# ** test: flask_api_context_handle_response
def test_flask_api_context_handle_response(flask_api_context: FlaskApiContext):
    '''
    Test the handle_response method.

    :param flask_api_context: A FlaskApiContext instance.
    :type flask_api_context: FlaskApiContext
    '''

    # Create a new request context.
    request_context = flask_api_context.parse_request(
        headers={'Content-Type': 'application/json'},
        data={'key': 'value'},
        feature_id='test_feature'
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

# ** test: flask_api_context_build_blueprint
def test_flask_api_context_build_blueprint(
    flask_api_context: FlaskApiContext,
    sample_blueprint_aggregate: FlaskBlueprintAggregate
):
    '''
    Test the build_blueprint method.

    :param flask_api_context: A FlaskApiContext instance.
    :type flask_api_context: FlaskApiContext
    :param sample_blueprint_aggregate: A sample blueprint aggregate.
    :type sample_blueprint_aggregate: FlaskBlueprintAggregate
    '''

    # Create a sample view function.
    def sample_view_func():
        return 'Sample Response'

    # Build a sample blueprint.
    blueprint = flask_api_context.build_blueprint(
        flask_blueprint=sample_blueprint_aggregate,
        view_func=sample_view_func
    )

    # Assert the blueprint was created correctly.
    assert isinstance(blueprint, Blueprint)
    assert blueprint.name == 'sample_blueprint'
    assert blueprint.url_prefix is None

# ** test: flask_api_context_build_flask_app
def test_flask_api_context_build_flask_app(flask_api_context: FlaskApiContext):
    '''
    Test the build_flask_app method.

    :param flask_api_context: A FlaskApiContext instance.
    :type flask_api_context: FlaskApiContext
    '''

    # Create a sample view function.
    def sample_view_func():
        return 'Sample Response'

    # Build a sample Flask app.
    flask_api_context.build_flask_app(
        view_func=sample_view_func
    )

    # Assert the Flask app was created.
    assert isinstance(flask_api_context.flask_app, Flask)

    # Assert the blueprints handler was called.
    flask_api_context.get_blueprints_handler.assert_called_once()
