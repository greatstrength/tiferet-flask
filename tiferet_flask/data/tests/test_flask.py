# *** imports

# ** core
from typing import List

# ** infra
import pytest

# ** app
from ..flask import *


# *** fixtures

# ** fixture: flask_blueprint_yaml_data_raw
@pytest.fixture
def flask_blueprint_yaml_data_raw() -> dict:
    '''
    A fixture that provides a sample raw dictionary representing a FlaskBlueprintYamlData instance.

    :return: A sample raw dictionary for FlaskBlueprintYamlData.
    :rtype: dict
    '''

    return {
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

# ** fixture: flask_blueprint_yaml_data
@pytest.fixture
def flask_blueprint_yaml_data(flask_blueprint_yaml_data_raw: dict) -> List[FlaskBlueprintYamlData]:
    '''
    A fixture that provides a sample list of FlaskBlueprintYamlData instances for testing.

    :param flask_blueprint_yaml_data_raw: A sample raw dictionary for FlaskBlueprintYamlData.
    :type flask_blueprint_yaml_data_raw: dict
    :return: A list of sample FlaskBlueprintYamlData instances.
    :rtype: List[FlaskBlueprintYamlData]
    '''

    return [
        FlaskBlueprintYamlData.from_data(
            id=id,
            **blueprint
        ) for id, blueprint in flask_blueprint_yaml_data_raw.items()
    ]

# *** tests

# ** test: flask_blueprint_yaml_data_creation
def test_flask_blueprint_yaml_data_creation(flask_blueprint_yaml_data: List[FlaskBlueprintYamlData]):
    '''
    Test the creation of FlaskBlueprintYamlData instances.

    :param flask_blueprint_yaml_data: A list of sample FlaskBlueprintYamlData instances.
    :type flask_blueprint_yaml_data: List[FlaskBlueprintYamlData]
    '''

    assert len(flask_blueprint_yaml_data) == 1

    blueprint = flask_blueprint_yaml_data[0]
    assert blueprint.id == 'sample_blueprint'
    assert blueprint.name == 'Sample Blueprint'
    assert len(blueprint.routes) == 1

    route = blueprint.routes['sample_route']
    assert route.id == 'sample_route'
    assert route.rule == '/sample'
    assert route.methods == ['GET', 'POST'] 

# ** test: flask_blueprint_yaml_data_map
def test_flask_blueprint_yaml_data_map(flask_blueprint_yaml_data: List[FlaskBlueprintYamlData]):
    '''
    Test the mapping of FlaskBlueprintYamlData instances to FlaskBlueprintContract instances.

    :param flask_blueprint_yaml_data: A list of sample FlaskBlueprintYamlData instances.
    :type flask_blueprint_yaml_data: List[FlaskBlueprintYamlData]
    '''

    models = [blueprint.map() for blueprint in flask_blueprint_yaml_data]
    assert len(models) == 1

    model = models[0]
    assert model.id == 'sample_blueprint'
    assert model.name == 'Sample Blueprint'
    assert len(model.routes) == 1

    route = model.routes[0]
    assert route.id == 'sample_route'
    assert route.rule == '/sample'
    assert route.methods == ['GET', 'POST'] 