# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from ....models import (
    FlaskBlueprint,
    FlaskRoute
)
from ....data import FlaskBlueprintYamlData
from ..flask import *

# *** fixtures

# ** fixture: yaml_data
@pytest.fixture
def yaml_data():
    '''
    Fixture to provide sample YAML data for flask configurations.
    '''
    return {
        'flask': {
            'blueprints': {
                'sample_blueprint': {
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

# ** fixture: flask_yaml_proxy
@pytest.fixture
def flask_yaml_proxy(yaml_data):
    '''
    Fixture to create a FlaskYamlProxy instance with mocked YAML loading.
    '''
    # Create a FlaskYamlProxy instance with a mock YAML file.
    proxy = FlaskYamlProxy(flask_config_file='flask.yml')

    # Mock the load_yaml method to return the sample YAML data.
    proxy.load_yaml = mock.Mock(return_value=[FlaskBlueprintYamlData.from_data(
        name=name, **blueprint
    ) for name, blueprint in yaml_data.get('flask', {}).get('blueprints', {}).items(
    )])

    # Return the proxy instance for use in tests.
    return proxy

# *** tests

# ** test: flask_yaml_proxy_load_yaml_success
def test_flask_yaml_proxy_load_yaml_success(yaml_data):
    '''
    Test successful loading of YAML data by FlaskYamlProxy.
    '''
    # Create a FlaskYamlProxy instance with a mock YAML file.
    proxy = FlaskYamlProxy(flask_config_file='flask.yml')

    # Mock the load_yaml method to return the sample YAML data.
    with mock.patch.object(YamlConfigurationProxy, 'load_yaml', return_value=yaml_data) as mock_load:
        result = proxy.load_yaml(start_node=lambda data: data.get('flask', {}))

    # Assert that the result matches the expected YAML data and the mock was called once.
    assert result == yaml_data
    mock_load.assert_called_once()

# ** test: flask_yaml_proxy_load_yaml_error
def test_flask_yaml_proxy_load_yaml_error():
    '''
    Test error handling in FlaskYamlProxy load_yaml for invalid YAML.
    '''
    # Create a FlaskYamlProxy instance with a mock YAML file.
    proxy = FlaskYamlProxy(flask_config_file='flask.yml')

    # Mock the load_yaml method to raise an exception for invalid YAML.
    with mock.patch.object(YamlConfigurationProxy, 'load_yaml', side_effect=Exception('Invalid YAML')):
        with pytest.raises(TiferetError) as exc_info:
            proxy.load_yaml(start_node=lambda data: data.get('flask', {}).get('blueprints', {}))

    # Assert that the exception is raised with the correct error code and message.
    assert exc_info.value.error_code == 'FLASK_CONFIG_LOADING_FAILED'
    assert 'Unable to load flask configuration file' in str(exc_info.value)

# ** test: flask_yaml_proxy_get_blueprints
def test_flask_yaml_proxy_get_blueprints(flask_yaml_proxy):
    '''
    Test the get_blueprints method of FlaskYamlProxy.
    '''
    # Call the get_blueprints method to retrieve blueprints.
    blueprints = flask_yaml_proxy.get_blueprints()

    # Assert that the returned blueprints are as expected.
    assert isinstance(blueprints, List)
    assert len(blueprints) == 1
    assert isinstance(blueprints[0], FlaskBlueprint)
    assert blueprints[0].name == 'sample_blueprint'
    assert blueprints[0].routes[0].rule == '/sample'
    assert blueprints[0].routes[0].methods == ['GET', 'POST']
    assert blueprints[0].routes[0].status_code == 269

# ** test: flask_yaml_proxy_get_route
def test_flask_yaml_proxy_get_route(flask_yaml_proxy):
    '''
    Test the get_route method of FlaskYamlProxy.
    '''
    # Call the get_route method to retrieve a specific route.
    route = flask_yaml_proxy.get_route(route_id='sample_route', blueprint_name='sample_blueprint')

    # Assert that the returned route is as expected.
    assert isinstance(route, FlaskRoute)
    assert route.id == 'sample_route'
    assert route.rule == '/sample'
    assert route.methods == ['GET', 'POST']
    assert route.status_code == 269

# ** test: flask_yaml_proxy_get_status_code
def test_flask_yaml_proxy_get_status_code(flask_yaml_proxy, yaml_data):
    '''
    Test the get_status_code method of FlaskYamlProxy.
    '''

    # Create a FlaskYamlProxy instance with mocked YAML loading.
    flask_yaml_proxy.load_yaml = mock.Mock(return_value=yaml_data.get('flask', {}).get('errors', {}))
    
    # Call the get_status_code method to retrieve a status code for a known error.
    status_code = flask_yaml_proxy.get_status_code('TEST_ERROR')

    # Assert that the returned status code is as expected.
    assert status_code == 420

    # Call the get_status_code method to retrieve a status code for an unknown error.
    default_status_code = flask_yaml_proxy.get_status_code('UNKNOWN_ERROR')

    # Assert that the default status code is returned for unknown errors.
    assert default_status_code == 500