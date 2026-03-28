# *** imports

# ** core
from typing import Dict, Any, List

# ** infra
from tiferet import (
    DomainObject,
    StringType,
    DictType,
    ModelType,
    Aggregate,
    TransferObject
)

# ** app
from ..domain import (
    FlaskRoute,
    FlaskBlueprint
)

# *** mappers

# ** mapper: flask_route_aggregate
class FlaskRouteAggregate(FlaskRoute, Aggregate):
    '''
    A mutable aggregate for Flask route domain objects.
    '''

    # * method: new
    @staticmethod
    def new(
        validate: bool = True,
        strict: bool = True,
        **kwargs
    ) -> 'FlaskRouteAggregate':
        '''
        Initializes a new Flask route aggregate.

        :param validate: True to validate the aggregate object.
        :type validate: bool
        :param strict: True to enforce strict mode.
        :type strict: bool
        :param kwargs: Keyword arguments.
        :type kwargs: dict
        :return: A new Flask route aggregate.
        :rtype: FlaskRouteAggregate
        '''

        # Create a new Flask route aggregate.
        return Aggregate.new(
            FlaskRouteAggregate,
            validate=validate,
            strict=strict,
            **kwargs
        )

# ** mapper: flask_blueprint_aggregate
class FlaskBlueprintAggregate(FlaskBlueprint, Aggregate):
    '''
    A mutable aggregate for Flask blueprint domain objects.
    '''

    # * method: new
    @staticmethod
    def new(
        validate: bool = True,
        strict: bool = True,
        **kwargs
    ) -> 'FlaskBlueprintAggregate':
        '''
        Initializes a new Flask blueprint aggregate.

        :param validate: True to validate the aggregate object.
        :type validate: bool
        :param strict: True to enforce strict mode.
        :type strict: bool
        :param kwargs: Keyword arguments.
        :type kwargs: dict
        :return: A new Flask blueprint aggregate.
        :rtype: FlaskBlueprintAggregate
        '''

        # Create a new Flask blueprint aggregate.
        return Aggregate.new(
            FlaskBlueprintAggregate,
            validate=validate,
            strict=strict,
            **kwargs
        )

    # * method: add_route
    def add_route(self, route: FlaskRoute) -> None:
        '''
        Add a route to the blueprint.

        :param route: The route to add.
        :type route: FlaskRoute
        '''

        # Append the route and validate.
        self.routes.append(route)
        self.validate()

    # * method: remove_route
    def remove_route(self, route_id: str) -> None:
        '''
        Remove a route from the blueprint by its ID.

        :param route_id: The ID of the route to remove.
        :type route_id: str
        '''

        # Filter out the route with the specified ID.
        self.routes = [r for r in self.routes if r.id != route_id]
        self.validate()

# ** mapper: flask_route_yaml_object
class FlaskRouteYamlObject(FlaskRoute, TransferObject):
    '''
    A YAML transfer object for Flask route data.
    '''

    class Options():
        '''
        Options for the transfer object.
        '''

        serialize_when_none = False
        roles = {
            'to_model': TransferObject.allow(),
            'to_data': TransferObject.deny('id')
        }

    # * attribute: id
    id = StringType(
        metadata=dict(
            description='The unique identifier of the route endpoint.'
        )
    )

    # * method: map
    def map(self, **kwargs) -> FlaskRouteAggregate:
        '''
        Map the YAML data to a FlaskRouteAggregate.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A Flask route aggregate.
        :rtype: FlaskRouteAggregate
        '''

        # Map the transfer object to an aggregate.
        return super().map(
            FlaskRouteAggregate,
            **kwargs
        )

# ** mapper: flask_blueprint_yaml_object
class FlaskBlueprintYamlObject(FlaskBlueprint, TransferObject):
    '''
    A YAML transfer object for Flask blueprint data.
    '''

    class Options():
        '''
        Options for the transfer object.
        '''

        serialize_when_none = False
        roles = {
            'to_model': TransferObject.deny('routes'),
            'to_data': TransferObject.deny('name')
        }

    # * attribute: name
    name = StringType(
        metadata=dict(
            description='The name of the blueprint.'
        )
    )

    # * attribute: routes
    routes = DictType(
        ModelType(FlaskRouteYamlObject),
        default={},
        metadata=dict(
            description='A dictionary of route ID to FlaskRouteYamlObject instances.'
        )
    )

    # * method: from_data
    @staticmethod
    def from_data(routes: Dict[str, Any] = {}, **kwargs) -> 'FlaskBlueprintYamlObject':
        '''
        Create a FlaskBlueprintYamlObject instance from raw data.

        :param routes: A dictionary of route ID to route data.
        :type routes: Dict[str, Any]
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new FlaskBlueprintYamlObject instance.
        :rtype: FlaskBlueprintYamlObject
        '''

        # Convert each route in the routes dictionary to a FlaskRouteYamlObject.
        route_objs = {id: TransferObject.from_data(
            FlaskRouteYamlObject,
            id=id, **data
        ) for id, data in routes.items()}

        # Create the blueprint transfer object.
        return TransferObject.from_data(
            FlaskBlueprintYamlObject,
            routes=route_objs,
            **kwargs
        )

    # * method: map
    def map(self, **kwargs) -> FlaskBlueprintAggregate:
        '''
        Map the YAML data to a FlaskBlueprintAggregate.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A Flask blueprint aggregate.
        :rtype: FlaskBlueprintAggregate
        '''

        # Map routes from dict to list, passing the dict key as the route id.
        return super().map(
            FlaskBlueprintAggregate,
            routes=[route.map(id=id) for id, route in self.routes.items()],
            **kwargs
        )

    # * method: from_model
    @staticmethod
    def from_model(blueprint: FlaskBlueprint, **kwargs) -> 'FlaskBlueprintYamlObject':
        '''
        Creates a FlaskBlueprintYamlObject from a FlaskBlueprint aggregate.

        :param blueprint: The blueprint aggregate.
        :type blueprint: FlaskBlueprint
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new FlaskBlueprintYamlObject.
        :rtype: FlaskBlueprintYamlObject
        '''

        # Convert routes list to dict keyed by route ID.
        return TransferObject.from_model(
            FlaskBlueprintYamlObject,
            blueprint,
            routes={
                route.id: TransferObject.from_model(FlaskRouteYamlObject, route)
                for route in blueprint.routes
            },
            **kwargs,
        )
