# *** imports

# ** infra
import pytest
from unittest import mock
from flask import Flask, Blueprint
from tiferet import (
    ModelObject
)

# ** app
from ..flask import *
from ...models import (
    FlaskBlueprint,
    FlaskRoute
)

# *** fixtures

# ** fixture: flask_blueprint
@pytest.fixture
def flask_blueprint() -> FlaskBlueprint:
    '''
    Fixture to provide a sample FlaskBlueprint instance for testing.
    '''

    return ModelObject.new(
        FlaskBlueprint,
        name='sample_blueprint',
        routes=[
            ModelObject.new(
                FlaskRoute,
                id='sample_route',
                rule='/sample',
                methods=['GET', 'POST'],
                status_code=224
            )
        ]
    )

# ** fixture: flask_api_context
@pytest.fixture
def flask_api_context(flask_blueprint: FlaskBlueprint) -> FlaskApiContext:
    '''
    Fixture to provide a FlaskApiContext instance for testing.
    '''

    # Create a mock feature context.
    mock_features = mock.Mock(spec=FeatureContext)

    # Create a mock error context.
    mock_errors = mock.Mock(spec=ErrorContext)
    mock_errors.handle_error.return_value = {'message': 'An error occurred.'}

    # Create a mock logging context.
    mock_logging = mock.Mock(spec=LoggingContext)

    # Create a mock FlaskApiHandler.
    mock_handler = mock.Mock(spec=FlaskApiHandler)
    mock_handler.get_blueprints.return_value = [flask_blueprint]
    mock_handler.get_status_code.return_value = 420
    mock_handler.get_route.return_value = ModelObject.new(
        FlaskRoute,
        id='sample_route',
        rule='/sample',
        methods=['GET', 'POST'],
        status_code=269
    )

    # Create and return the FlaskApiContext instance.
    return FlaskApiContext(
        interface_id='test_flask',
        features=mock_features,
        errors=mock_errors,
        logging=mock_logging,
        flask_api_handler=mock_handler
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
    Test the handle_error method of FlaskApiContext.

    :param flask_api_context: A FlaskApiContext instance.
    :type flask_api_context: FlaskApiContext
    '''

    # Create a sample exception.
    sample_exception = Exception('Sample error')

    response, status_code = flask_api_context.handle_error(sample_exception)

    # Assert that the response is a tuple of (response, status_code).
    assert isinstance(response, dict)
    assert status_code == 500 

# ** test: flask_api_context_handle_tiferet_error
def test_flask_api_context_handle_tiferet_error(flask_api_context: FlaskApiContext):
    '''
    Test the handle_error method of FlaskApiContext with a TiferetError.

    :param flask_api_context: A FlaskApiContext instance.
    :type flask_api_context: FlaskApiContext
    '''

    # Create a sample TiferetError.
    sample_tiferet_error = TiferetError('TEST_ERROR', 'A test Tiferet error occurred.')

    # Mock the error handler to return a specific response.
    flask_api_context.errors.handle_error.return_value = {'error_code': 'TEST_ERROR', 'text': 'A test Tiferet error occurred.'}

    # Call the handle_error method.
    response, status_code = flask_api_context.handle_error(sample_tiferet_error)

    # Assert that the response is a tuple of (response, status_code).
    assert response == {
        'error_code': 'TEST_ERROR',
        'text': 'A test Tiferet error occurred.'
    }
    assert status_code == 420

# ** test: flask_api_context_handle_response
def test_flask_api_context_handle_response(flask_api_context: FlaskApiContext):

    # Create a new request context from the flask_api_context.
    request_context = flask_api_context.parse_request(
        headers={'Content-Type': 'application/json'},
        data={'key': 'value'},
        feature_id='test_feature'
    )

    # Set a sample result in the request context.
    request_context.set_result({'result_key': 'result_value'})

    # Handle the response.
    response, status_code = flask_api_context.handle_response(request_context)

    # Assert that the response is as expected.
    assert response == {'result_key': 'result_value'}
    assert status_code == 269

# ** test: flask_api_context_build_blueprint
def test_flask_api_context_build_blueprint(flask_api_context: FlaskApiContext, flask_blueprint: FlaskBlueprint):
    '''
    Test the build_blueprint method of FlaskApiContext.

    :param flask_api_context: A FlaskApiContext instance.
    :type flask_api_context: FlaskApiContext
    '''

    # Create a sample view function.
    def sample_view_func():
        return 'Sample Response'

    # Build a sample blueprint.
    blueprint = flask_api_context.build_blueprint(
        flask_blueprint=flask_blueprint,
        view_func=sample_view_func
    )

    # Assert that the returned object is a FlaskBlueprint instance.
    assert isinstance(blueprint, Blueprint)
    assert blueprint.name == 'sample_blueprint'
    assert blueprint.url_prefix is None

# ** test: flask_api_context_build_flask_app
def test_flask_api_context_build_flask_app(flask_api_context: FlaskApiContext):
    '''
    Test the build_flask_app method of FlaskApiContext.

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

    # Assert that the returned object is a Flask instance.
    assert isinstance(flask_api_context.flask_app, Flask)