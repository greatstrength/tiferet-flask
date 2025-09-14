# *** imports

# ** infra
import pytest

# ** app
from ...models.flask import *

# *** fixtures

# ** fixture: flask_route
@pytest.fixture
def flask_route() -> FlaskRoute:
    '''
    A fixture that provides a sample FlaskRoute instance for testing.
    
    :return: A sample FlaskRoute instance.
    :rtype: FlaskRoute
    '''
    
    return ModelObject.new(
        FlaskRoute,
        id='sample_route',
        rule='/sample',
        methods=['GET', 'POST'],
        status_code=200
    )

# ** fixture: flask_blueprint
@pytest.fixture
def flask_blueprint(flask_route: FlaskRoute) -> FlaskBlueprint: 
    '''
    A fixture that provides a sample FlaskBlueprint instance for testing.
    
    :param flask_route: A sample FlaskRoute instance.
    :type flask_route: FlaskRoute
    :return: A sample FlaskBlueprint instance.
    :rtype: FlaskBlueprint
    '''
    
    return ModelObject.new(
        FlaskBlueprint,
        id='sample_blueprint',
        routes=[flask_route]
    )

# *** tests

# ** test: flask_route_creation
def test_flask_route_creation(flask_route: FlaskRoute):
    '''
    Test the creation of a FlaskRoute instance.
    
    :param flask_route: A sample FlaskRoute instance.
    :type flask_route: FlaskRoute
    '''
    
    assert flask_route.id == 'sample_route'
    assert flask_route.rule == '/sample'
    assert flask_route.methods == ['GET', 'POST']
    assert flask_route.status_code == 200

# ** test: flask_blueprint_creation
def test_flask_blueprint_creation(flask_blueprint: FlaskBlueprint, flask_route: FlaskRoute):
    '''
    Test the creation of a FlaskBlueprint instance.
    
    :param flask_blueprint: A sample FlaskBlueprint instance.
    :type flask_blueprint: FlaskBlueprint
    :param flask_route: A sample FlaskRoute instance.
    :type flask_route: FlaskRoute
    '''
    
    assert flask_blueprint.id == 'sample_blueprint'
    assert len(flask_blueprint.routes) == 1
    assert flask_blueprint.routes[0] == flask_route