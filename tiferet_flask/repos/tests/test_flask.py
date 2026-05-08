# *** imports

# ** core
from pathlib import Path

# ** infra
import pytest
import yaml

# ** app
from ..flask import FlaskYamlRepository
from ...domain import FlaskBlueprint, FlaskRoute

# *** fixtures

# ** fixture: flask_yaml_content
@pytest.fixture
def flask_yaml_content() -> dict:
    '''
    Sample YAML content for Flask configuration.

    :return: A dictionary representing Flask YAML configuration.
    :rtype: dict
    '''

    return {
        'flask': {
            'blueprints': {
                'sample_blueprint': {
                    'url_prefix': '/api',
                    'routes': {
                        'sample_route': {
                            'rule': '/sample',
                            'methods': ['GET', 'POST'],
                            'status_code': 269
                        }
                    }
                }
            },
            'errors': {
                'TEST_ERROR': 420
            }
        }
    }

# ** fixture: flask_yaml_file
@pytest.fixture
def flask_yaml_file(tmp_path: Path, flask_yaml_content: dict) -> str:
    '''
    Create a temporary YAML file with Flask configuration.

    :param tmp_path: Pytest temporary directory.
    :type tmp_path: Path
    :param flask_yaml_content: The YAML content to write.
    :type flask_yaml_content: dict
    :return: The path to the temporary YAML file.
    :rtype: str
    '''

    # Write the YAML content to a temporary file.
    yaml_path = tmp_path / 'flask.yml'
    yaml_path.write_text(yaml.dump(flask_yaml_content), encoding='utf-8')

    # Return the path as a string.
    return str(yaml_path)

# ** fixture: flask_repo
@pytest.fixture
def flask_repo(flask_yaml_file: str) -> FlaskYamlRepository:
    '''
    Create a FlaskYamlRepository instance for testing.

    :param flask_yaml_file: Path to the temporary YAML file.
    :type flask_yaml_file: str
    :return: A FlaskYamlRepository instance.
    :rtype: FlaskYamlRepository
    '''

    return FlaskYamlRepository(flask_yaml_file=flask_yaml_file)

# *** tests

# ** test: flask_repo_get_blueprints
def test_flask_repo_get_blueprints(flask_repo: FlaskYamlRepository):
    '''
    Test retrieving all Flask blueprints.
    '''

    # Retrieve blueprints.
    blueprints = flask_repo.get_blueprints()

    # Assert structure and values.
    assert len(blueprints) == 1
    assert isinstance(blueprints[0], FlaskBlueprint)
    assert blueprints[0].name == 'sample_blueprint'
    assert blueprints[0].url_prefix == '/api'
    assert len(blueprints[0].routes) == 1
    assert blueprints[0].routes[0].id == 'sample_route'
    assert blueprints[0].routes[0].endpoint == 'sample_blueprint.sample_route'
    assert blueprints[0].routes[0].rule == '/sample'
    assert blueprints[0].routes[0].methods == ['GET', 'POST']
    assert blueprints[0].routes[0].status_code == 269

# ** test: flask_repo_get_route
def test_flask_repo_get_route(flask_repo: FlaskYamlRepository):
    '''
    Test retrieving a specific Flask route.
    '''

    # Retrieve route by ID and blueprint name.
    route = flask_repo.get_route(
        route_id='sample_route',
        blueprint_name='sample_blueprint',
    )

    # Assert route values.
    assert isinstance(route, FlaskRoute)
    assert route.id == 'sample_route'
    assert route.endpoint == 'sample_blueprint.sample_route'
    assert route.rule == '/sample'
    assert route.methods == ['GET', 'POST']
    assert route.status_code == 269

# ** test: flask_repo_get_route_without_blueprint
def test_flask_repo_get_route_without_blueprint(flask_repo: FlaskYamlRepository):
    '''
    Test retrieving a route without specifying a blueprint name.
    '''

    # Retrieve route by ID only.
    route = flask_repo.get_route(route_id='sample_route')

    # Assert route is found.
    assert route is not None
    assert route.id == 'sample_route'

# ** test: flask_repo_get_route_not_found
def test_flask_repo_get_route_not_found(flask_repo: FlaskYamlRepository):
    '''
    Test that get_route returns None for a nonexistent route.
    '''

    route = flask_repo.get_route(route_id='nonexistent_route')
    assert route is None

# ** test: flask_repo_get_status_code
def test_flask_repo_get_status_code(flask_repo: FlaskYamlRepository):
    '''
    Test retrieving a status code for a known error code.
    '''

    status_code = flask_repo.get_status_code('TEST_ERROR')
    assert status_code == 420

# ** test: flask_repo_get_status_code_default
def test_flask_repo_get_status_code_default(flask_repo: FlaskYamlRepository):
    '''
    Test that an unknown error code returns the default 500 status.
    '''

    status_code = flask_repo.get_status_code('UNKNOWN_ERROR')
    assert status_code == 500
