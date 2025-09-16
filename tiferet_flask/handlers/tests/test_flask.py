# *** imports

# ** infra
import pytest
from unittest import mock
from tiferet import (
    ModelObject,
    TiferetError
)

# ** app
from ...models import (
    FlaskBlueprint,
    FlaskRoute
)
from ..flask import (
    FlaskApiHandler,
    FlaskApiRepository
)

# *** fixtures

# ** fixture: blueprints
@pytest.fixture
def blueprints():
    """Fixture to provide a mock Error object."""
    
    return [
        ModelObject.new(
            FlaskBlueprint,
            name='sample_blueprint',
            routes=[
                ModelObject.new(
                    FlaskRoute,
                    id='sample_route',
                    rule='/sample',
                    methods=['GET', 'POST'],
                    status_code=269
                )
            ]
        )
    ]

# ** fixture: flask_repo
@pytest.fixture()
def flask_repo(blueprints):
    """Fixture to provide a mock ErrorRepository."""
    
    repo = mock.Mock(spec=FlaskApiRepository)

    repo.get_blueprints.return_value = blueprints
    repo.get_route.return_value = blueprints[0].routes[0]
    repo.get_status_code.return_value = 420

    return repo

# ** fixture: flask_handler
@pytest.fixture
def flask_handler(flask_repo):
    """Fixture to provide an ErrorHandler instance."""
    
    return FlaskApiHandler(
        flask_repo=flask_repo,
    )

# *** tests

# ** test: get_blueprints
def test_get_blueprints(flask_handler, blueprints):
    '''Test the get_blueprints method of FlaskApiHandler.'''

    # Call the get_blueprints method to get the blueprints
    loaded_flasks = flask_handler.get_blueprints()

    # Assert that the returned blueprints match the mock data
    assert loaded_flasks == blueprints

# ** test: get_route_error
def test_get_route_error(flask_handler, flask_repo):
    '''Test the get_route method of FlaskApiHandler when route is not found.'''

    # Mock the get_route method to return None
    flask_repo.get_route.return_value = None

    # Assert that calling get_route raises an error
    with pytest.raises(TiferetError) as exc_info:
        flask_handler.get_route('non_existent_route')

    # Optionally, check the exception message
    assert exc_info.value.error_code == 'FLASK_ROUTE_NOT_FOUND'
    assert 'Flask route not found for endpoint' in str(exc_info.value)

# ** test: get_route
def test_get_route(flask_handler, blueprints):
    '''Test the get_route method of FlaskApiHandler.'''

    # Call the get_route method to get a specific route
    route = flask_handler.get_route('sample_route')

    # Assert that the returned route matches the mock data
    assert route == blueprints[0].routes[0]

# ** test: get_status_code
def test_get_status_code(flask_handler, flask_repo):
    '''Test the get_status_code method of FlaskApiHandler.'''

    # Call the get_status_code method to get a status code for a known error
    status_code = flask_handler.get_status_code('TEST_ERROR')

    # Assert that the returned status code matches the mock data
    assert status_code == 420