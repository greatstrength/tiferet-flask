# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from ....data.flask import FlaskBlueprintYamlData
from ....models.flask import FlaskBlueprint
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
                    'name': 'Sample Blueprint',
                    'routes': {
                        'sample_route': {
                            'rule': '/sample',
                            'methods': ['GET', 'POST']
                        }
                    }
                }
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
        id=id, **blueprint
    ) for id, blueprint in yaml_data.get('flask', {}).get('blueprints', {}).items(
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
    assert blueprints[0].id == 'sample_blueprint'
    assert blueprints[0].name == 'Sample Blueprint'
    assert blueprints[0].routes[0].rule == '/sample'
    assert blueprints[0].routes[0].methods == ['GET', 'POST']