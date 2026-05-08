"""Flask mappers."""

# *** imports

# ** core
from typing import Any, ClassVar, Dict, List

# ** infra
from pydantic import Field

# ** app
from ..domain import (
    FlaskRoute,
    FlaskBlueprint,
)
from tiferet.mappers import (
    Aggregate,
    TransferObject,
)

# *** mappers

# ** mapper: flask_route_aggregate
class FlaskRouteAggregate(FlaskRoute, Aggregate):
    '''
    Aggregate for the FlaskRoute domain object.
    '''

    pass

# ** mapper: flask_blueprint_aggregate
class FlaskBlueprintAggregate(FlaskBlueprint, Aggregate):
    '''
    Aggregate for the FlaskBlueprint domain object.
    '''

    # * method: add_route
    def add_route(self,
            endpoint: str,
            rule: str,
            methods: List[str],
            status_code: int = 200,
        ) -> FlaskRouteAggregate:
        '''
        Add a new route to the blueprint.

        :param endpoint: The unique identifier of the route endpoint.
        :type endpoint: str
        :param rule: The URL rule as string.
        :type rule: str
        :param methods: A list of HTTP methods this rule should be limited to.
        :type methods: List[str]
        :param status_code: The default HTTP status code for the route response.
        :type status_code: int
        :return: The created route aggregate.
        :rtype: FlaskRouteAggregate
        '''

        # Create the route aggregate.
        route = FlaskRouteAggregate(
            id=endpoint,
            endpoint=f'{self.name}.{endpoint}',
            rule=rule,
            methods=methods,
            status_code=status_code,
        )

        # Copy routes to a local list, append, and reassign.
        routes = list(self.routes)
        routes.append(route)
        self.routes = routes

        # Return the created route.
        return route

    # * method: remove_route
    def remove_route(self, route_id: str) -> None:
        '''
        Remove a route from the blueprint by its ID.

        :param route_id: The ID of the route to remove.
        :type route_id: str
        '''

        # Filter out the route with the specified ID and reassign.
        self.routes = [r for r in self.routes if r.id != route_id]

# ** mapper: flask_route_yaml_object
class FlaskRouteYamlObject(FlaskRoute, TransferObject):
    '''
    A YAML data representation of a FlaskRoute object.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {},
        'to_data.yaml': {'exclude': {'id', 'endpoint'}},
    }

    # * attribute: id
    id: str | None = Field(
        default=None,
        description='The unique identifier of the route (provided via dict key during mapping).',
    )

    # * attribute: endpoint
    endpoint: str | None = Field(
        default=None,
        description='The fully-qualified endpoint (blueprint_name.route_id).',
    )

    # * method: map
    def map(self, id: str = None, endpoint: str = None, **overrides) -> FlaskRouteAggregate:
        '''
        Map the YAML data to a FlaskRouteAggregate.

        :param id: The route identifier override.
        :type id: str
        :param endpoint: The endpoint override.
        :type endpoint: str
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new FlaskRouteAggregate.
        :rtype: FlaskRouteAggregate
        '''

        # Map to the route aggregate with overrides.
        return super().map(
            FlaskRouteAggregate,
            id=id,
            endpoint=endpoint,
            **overrides,
        )

    # * method: from_model
    @classmethod
    def from_model(cls, route: FlaskRoute, **overrides) -> 'FlaskRouteYamlObject':
        '''
        Create a FlaskRouteYamlObject from a FlaskRoute model.

        :param route: The FlaskRoute model.
        :type route: FlaskRoute
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new FlaskRouteYamlObject.
        :rtype: FlaskRouteYamlObject
        '''

        # Create from the model.
        return super().from_model(route, **overrides)

# ** mapper: flask_blueprint_yaml_object
class FlaskBlueprintYamlObject(FlaskBlueprint, TransferObject):
    '''
    A YAML data representation of a FlaskBlueprint object.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {'exclude': {'routes'}},
        'to_data.yaml': {'by_alias': True, 'exclude': {'name'}},
    }

    # * attribute: name
    name: str | None = Field(
        default=None,
        description='The name of the blueprint.',
    )

    # * attribute: routes
    routes: Dict[str, FlaskRouteYamlObject] = Field(
        default_factory=dict,
        description='A dictionary of route ID to FlaskRouteYamlObject instances.',
    )

    # * method: map
    def map(self, **overrides) -> FlaskBlueprintAggregate:
        '''
        Map the YAML data to a FlaskBlueprintAggregate.

        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new FlaskBlueprintAggregate.
        :rtype: FlaskBlueprintAggregate
        '''

        # Map to the blueprint aggregate with nested route conversion.
        return super().map(
            FlaskBlueprintAggregate,
            routes=[
                route.map(id=id, endpoint=f'{self.name}.{id}')
                for id, route in self.routes.items()
            ],
            **overrides,
        )

    # * method: from_model
    @classmethod
    def from_model(cls, blueprint: FlaskBlueprint, **overrides) -> 'FlaskBlueprintYamlObject':
        '''
        Create a FlaskBlueprintYamlObject from a FlaskBlueprint model.

        :param blueprint: The FlaskBlueprint model.
        :type blueprint: FlaskBlueprint
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new FlaskBlueprintYamlObject.
        :rtype: FlaskBlueprintYamlObject
        '''

        # Create from the model, converting nested routes list to dict.
        return super().from_model(
            blueprint,
            routes={
                route.id: FlaskRouteYamlObject.from_model(route)
                for route in blueprint.routes
            },
            **overrides,
        )
