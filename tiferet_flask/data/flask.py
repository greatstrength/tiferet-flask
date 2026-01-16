# *** import

# ** core
from typing import Dict, Any

# ** infra
from tiferet import (
    DataObject,
    StringType,
    DictType,
    ModelType
)

# ** app
from ..models import (
    FlaskRoute, 
    FlaskBlueprint
)
from ..contracts import (
    FlaskRouteContract,
    FlaskBlueprintContract
)

# *** data

# ** data: flask_route_yaml_data
class FlaskRouteYamlData(DataObject, FlaskRoute):
    '''
    A data object for Flask route model from YAML.
    '''

    class Options():
        serialize_when_none = False
        roles = {
            'to_model': DataObject.allow(),
            'to_data': DataObject.deny('id')
        }

    # * attribute: id
    id = StringType(
        metadata=dict(
            description='The unique identifier of the route endpoint.'
        )
    )

    # * method: map
    def map(self, id: str) -> FlaskRouteContract:
        '''
        Map the data object to a FlaskRouteContract instance.

        :param id: The unique identifier of the route endpoint.
        :type id: str
        :return: A FlaskRouteContract instance.
        :rtype: FlaskRouteContract
        '''

        # Map the data object to a model instance.
        return super().map(
            FlaskRoute,
            id=id
        )

# ** data: flask_blueprint_yaml_data
class FlaskBlueprintYamlData(DataObject, FlaskBlueprint):
    '''
    A data object for Flask blueprint model from YAML.
    '''

    class Options():
        serialize_when_none = False
        roles = {
            'to_model': DataObject.deny('routes'),
            'to_data': DataObject.deny('name')
        }

    # * attribute: name
    name = StringType(
        metadata=dict(
            description='The name of the blueprint.'
        )
    )

    # * attribute: routes
    routes = DictType(
        ModelType(FlaskRouteYamlData),
        default={},
        metadata=dict(
            description='A dictionary of route ID to FlaskRouteYamlData instances.'
        )
    )

    # * method: from_data
    @staticmethod
    def from_data(routes: Dict[str, Any] = {}, **kwargs) -> 'FlaskBlueprintYamlData':
        '''
        Create a FlaskBlueprintYamlData instance from raw data.

        :param routes: A dictionary of route ID to route data.
        :type routes: Dict[str, Any]
        :return: A FlaskBlueprintYamlData instance.
        :rtype: FlaskBlueprintYamlData
        '''

        # Convert each route in the routes dictionary to a FlaskRouteYamlData instance.
        route_objs = {id: DataObject.from_data(
            FlaskRouteYamlData, 
            id=id, **data
        ) for id, data in routes.items()}

        # 
        return DataObject.from_data(
            FlaskBlueprintYamlData,
            routes=route_objs,
            **kwargs
        )

    # * method: map
    def map(self) -> FlaskBlueprintContract:
        '''
        Map the data object to a FlaskBlueprintContract instance.

        :return: A FlaskBlueprintContract instance.
        :rtype: FlaskBlueprintContract
        '''

        # Map each route in the routes dictionary.
        return super().map(
            FlaskBlueprint,
            routes=[route.map(id=id) for id, route in self.routes.items()]
        )