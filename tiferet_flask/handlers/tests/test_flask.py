# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from ..flask import (
    FlaskApiHandler,
    FlaskApiRepository
)
from ...models.flask import (
    ModelObject,
    FlaskBlueprint,
    FlaskRoute
)

# *** fixtures

# ** fixture: blueprints
@pytest.fixture
def blueprints():
    """Fixture to provide a mock Error object."""
    
    return [
        ModelObject.new(
            FlaskBlueprint,
            name='Sample Blueprint',
            id='sample_blueprint',
            routes=[
                ModelObject.new(
                    FlaskRoute,
                    id='sample_route',
                    rule='/sample',
                    methods=['GET', 'POST']
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

    return repo

# ** fixture: flask_handler
@pytest.fixture
def flask_handler(flask_repo):
    """Fixture to provide an ErrorHandler instance."""
    
    return FlaskApiHandler(
        flask_repo=flask_repo,
    )

# *** tests

# ** test: test_load_flasks
def test_load_flasks(flask_handler, blueprints):
    """Test the load_flasks method of ErrorHandler."""

    # Call the get_blueprints method to get the blueprints
    loaded_flasks = flask_handler.get_blueprints()

    # Assert that the returned blueprints match the mock data
    assert loaded_flasks == blueprints