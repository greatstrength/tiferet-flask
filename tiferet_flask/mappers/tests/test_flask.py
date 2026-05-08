# *** imports

# ** core
from typing import List

# ** infra
import pytest
from tiferet import TiferetError

# ** app
from ..flask import (
    FlaskRouteAggregate,
    FlaskBlueprintAggregate,
    FlaskRouteYamlObject,
    FlaskBlueprintYamlObject
)
from ...domain import FlaskRoute, FlaskBlueprint

# *** fixtures

# ** fixture: flask_route_aggregate
@pytest.fixture
def flask_route_aggregate() -> FlaskRouteAggregate:
    '''
    A fixture that provides a sample FlaskRouteAggregate.

    :return: A sample FlaskRouteAggregate.
    :rtype: FlaskRouteAggregate
    '''

    return FlaskRouteAggregate(
        id='sample_route',
        endpoint='sample_blueprint.sample_route',
        rule='/sample',
        methods=['GET', 'POST'],
        status_code=200,
    )

# ** fixture: flask_blueprint_aggregate
@pytest.fixture
def flask_blueprint_aggregate(flask_route_aggregate: FlaskRouteAggregate) -> FlaskBlueprintAggregate:
    '''
    A fixture that provides a sample FlaskBlueprintAggregate.

    :param flask_route_aggregate: A sample FlaskRouteAggregate.
    :type flask_route_aggregate: FlaskRouteAggregate
    :return: A sample FlaskBlueprintAggregate.
    :rtype: FlaskBlueprintAggregate
    '''

    return FlaskBlueprintAggregate(
        name='sample_blueprint',
        routes=[flask_route_aggregate],
    )

# ** fixture: flask_blueprint_yaml_data_raw
@pytest.fixture
def flask_blueprint_yaml_data_raw() -> dict:
    '''
    A fixture that provides sample raw YAML data.

    :return: Raw dictionary representing blueprint YAML data.
    :rtype: dict
    '''

    return {
        'sample_blueprint': {
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
def flask_blueprint_yaml_data(flask_blueprint_yaml_data_raw: dict) -> List[FlaskBlueprintYamlObject]:
    '''
    A fixture that provides FlaskBlueprintYamlObject instances from raw data.

    :param flask_blueprint_yaml_data_raw: Raw dictionary data.
    :type flask_blueprint_yaml_data_raw: dict
    :return: A list of FlaskBlueprintYamlObject instances.
    :rtype: List[FlaskBlueprintYamlObject]
    '''

    return [
        FlaskBlueprintYamlObject.model_validate(
            dict(name=name, **blueprint)
        ) for name, blueprint in flask_blueprint_yaml_data_raw.items()
    ]

# *** tests

# ** test: flask_route_aggregate_creation
def test_flask_route_aggregate_creation(flask_route_aggregate: FlaskRouteAggregate):
    '''
    Test the creation of a FlaskRouteAggregate.
    '''

    assert flask_route_aggregate.id == 'sample_route'
    assert flask_route_aggregate.endpoint == 'sample_blueprint.sample_route'
    assert flask_route_aggregate.rule == '/sample'
    assert flask_route_aggregate.methods == ['GET', 'POST']
    assert flask_route_aggregate.status_code == 200

# ** test: flask_route_aggregate_set_attribute
def test_flask_route_aggregate_set_attribute(flask_route_aggregate: FlaskRouteAggregate):
    '''
    Test valid set_attribute on FlaskRouteAggregate.
    '''

    flask_route_aggregate.set_attribute('rule', '/updated')
    assert flask_route_aggregate.rule == '/updated'

# ** test: flask_route_aggregate_set_attribute_invalid
def test_flask_route_aggregate_set_attribute_invalid(flask_route_aggregate: FlaskRouteAggregate):
    '''
    Test that set_attribute raises error for an invalid attribute.
    '''

    with pytest.raises(TiferetError):
        flask_route_aggregate.set_attribute('invalid_attr', 'value')

# ** test: flask_blueprint_aggregate_creation
def test_flask_blueprint_aggregate_creation(flask_blueprint_aggregate: FlaskBlueprintAggregate):
    '''
    Test the creation of a FlaskBlueprintAggregate.
    '''

    assert flask_blueprint_aggregate.name == 'sample_blueprint'
    assert len(flask_blueprint_aggregate.routes) == 1

# ** test: flask_blueprint_aggregate_add_route
def test_flask_blueprint_aggregate_add_route(flask_blueprint_aggregate: FlaskBlueprintAggregate):
    '''
    Test adding a route to a FlaskBlueprintAggregate.
    '''

    # Add a route using the new signature.
    route = flask_blueprint_aggregate.add_route(
        endpoint='new_route',
        rule='/new',
        methods=['DELETE'],
    )

    # Assert the route was added with correct endpoint.
    assert len(flask_blueprint_aggregate.routes) == 2
    assert route.id == 'new_route'
    assert route.endpoint == 'sample_blueprint.new_route'
    assert flask_blueprint_aggregate.routes[1].id == 'new_route'

# ** test: flask_blueprint_aggregate_remove_route
def test_flask_blueprint_aggregate_remove_route(flask_blueprint_aggregate: FlaskBlueprintAggregate):
    '''
    Test removing a route from a FlaskBlueprintAggregate.
    '''

    # Remove the route.
    flask_blueprint_aggregate.remove_route('sample_route')

    # Assert the route was removed.
    assert len(flask_blueprint_aggregate.routes) == 0

# ** test: flask_blueprint_yaml_data_creation
def test_flask_blueprint_yaml_data_creation(flask_blueprint_yaml_data: List[FlaskBlueprintYamlObject]):
    '''
    Test the creation of FlaskBlueprintYamlObject instances from raw data.
    '''

    assert len(flask_blueprint_yaml_data) == 1

    blueprint = flask_blueprint_yaml_data[0]
    assert blueprint.name == 'sample_blueprint'
    assert len(blueprint.routes) == 1

    route = blueprint.routes['sample_route']
    assert route.rule == '/sample'
    assert route.methods == ['GET', 'POST']

# ** test: flask_blueprint_yaml_data_map
def test_flask_blueprint_yaml_data_map(flask_blueprint_yaml_data: List[FlaskBlueprintYamlObject]):
    '''
    Test mapping FlaskBlueprintYamlObject instances to aggregates.
    '''

    aggregates = [blueprint.map() for blueprint in flask_blueprint_yaml_data]
    assert len(aggregates) == 1

    aggregate = aggregates[0]
    assert isinstance(aggregate, FlaskBlueprintAggregate)
    assert aggregate.name == 'sample_blueprint'
    assert len(aggregate.routes) == 1

    route = aggregate.routes[0]
    assert isinstance(route, FlaskRouteAggregate)
    assert route.id == 'sample_route'
    assert route.endpoint == 'sample_blueprint.sample_route'
    assert route.rule == '/sample'
    assert route.methods == ['GET', 'POST']

# ** test: flask_blueprint_yaml_object_from_model
def test_flask_blueprint_yaml_object_from_model(flask_blueprint_aggregate: FlaskBlueprintAggregate):
    '''
    Test creating a FlaskBlueprintYamlObject from an aggregate (round-trip).
    '''

    # Create a YAML object from the aggregate.
    yaml_obj = FlaskBlueprintYamlObject.from_model(flask_blueprint_aggregate)

    # Assert the YAML object is correctly formed.
    assert yaml_obj.name == 'sample_blueprint'
    assert 'sample_route' in yaml_obj.routes
    assert yaml_obj.routes['sample_route'].rule == '/sample'

# ** test: flask_blueprint_round_trip
def test_flask_blueprint_round_trip(flask_blueprint_aggregate: FlaskBlueprintAggregate):
    '''
    Test full round-trip: aggregate → YAML object → aggregate.
    '''

    # Convert aggregate to YAML object.
    yaml_obj = FlaskBlueprintYamlObject.from_model(flask_blueprint_aggregate)

    # Map back to aggregate.
    result = yaml_obj.map()

    # Assert the round-trip preserves data.
    assert isinstance(result, FlaskBlueprintAggregate)
    assert result.name == flask_blueprint_aggregate.name
    assert len(result.routes) == len(flask_blueprint_aggregate.routes)
    assert result.routes[0].id == flask_blueprint_aggregate.routes[0].id
    assert result.routes[0].endpoint == flask_blueprint_aggregate.routes[0].endpoint
    assert result.routes[0].rule == flask_blueprint_aggregate.routes[0].rule
    assert result.routes[0].methods == flask_blueprint_aggregate.routes[0].methods
