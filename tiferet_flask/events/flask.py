# *** imports

# ** core
from typing import List

# ** infra
from tiferet.events import DomainEvent

# ** app
from ..interfaces import FlaskApiService
from ..mappers import (
    FlaskBlueprintAggregate,
    FlaskRouteAggregate
)

# *** events

# ** event: get_flask_blueprints
class GetFlaskBlueprints(DomainEvent):
    '''
    A domain event to retrieve all Flask blueprints.
    '''

    # * attribute: flask_service
    flask_service: FlaskApiService

    # * init
    def __init__(self, flask_service: FlaskApiService):
        '''
        Initialize the GetFlaskBlueprints event.

        :param flask_service: The Flask API service.
        :type flask_service: FlaskApiService
        '''

        # Set the Flask API service dependency.
        self.flask_service = flask_service

    # * method: execute
    def execute(self, **kwargs) -> List[FlaskBlueprintAggregate]:
        '''
        Retrieve all Flask blueprints.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A list of Flask blueprint aggregates.
        :rtype: List[FlaskBlueprintAggregate]
        '''

        # Retrieve all blueprints from the service.
        blueprints = self.flask_service.get_blueprints()

        # Return the blueprints.
        return blueprints

# ** event: get_flask_route
class GetFlaskRoute(DomainEvent):
    '''
    A domain event to retrieve a Flask route by endpoint.
    '''

    # * attribute: flask_service
    flask_service: FlaskApiService

    # * init
    def __init__(self, flask_service: FlaskApiService):
        '''
        Initialize the GetFlaskRoute event.

        :param flask_service: The Flask API service.
        :type flask_service: FlaskApiService
        '''

        # Set the Flask API service dependency.
        self.flask_service = flask_service

    # * method: execute
    @DomainEvent.parameters_required(['endpoint'])
    def execute(self, endpoint: str, **kwargs) -> FlaskRouteAggregate:
        '''
        Retrieve a Flask route by its endpoint string.

        The endpoint is in the format 'blueprint_name.route_id' or just 'route_id'
        if no blueprint is specified.

        :param endpoint: The endpoint identifier (e.g., 'blueprint_name.route_id').
        :type endpoint: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The Flask route aggregate.
        :rtype: FlaskRouteAggregate
        '''

        # Parse the endpoint into blueprint name and route ID.
        blueprint_name = None
        try:
            blueprint_name, route_id = endpoint.split('.')
        except ValueError:
            route_id = endpoint

        # Retrieve the route from the service.
        route = self.flask_service.get_route(
            route_id=route_id,
            blueprint_name=blueprint_name,
        )

        # Verify that the route exists.
        self.verify(
            expression=route is not None,
            error_code='FLASK_ROUTE_NOT_FOUND',
            message=f'Flask route not found for endpoint: {endpoint}',
            endpoint=endpoint,
        )

        # Return the route.
        return route

# ** event: get_flask_status_code
class GetFlaskStatusCode(DomainEvent):
    '''
    A domain event to retrieve the HTTP status code for an error code.
    '''

    # * attribute: flask_service
    flask_service: FlaskApiService

    # * init
    def __init__(self, flask_service: FlaskApiService):
        '''
        Initialize the GetFlaskStatusCode event.

        :param flask_service: The Flask API service.
        :type flask_service: FlaskApiService
        '''

        # Set the Flask API service dependency.
        self.flask_service = flask_service

    # * method: execute
    @DomainEvent.parameters_required(['error_code'])
    def execute(self, error_code: str, **kwargs) -> int:
        '''
        Retrieve the HTTP status code for a given error code.

        :param error_code: The error code identifier.
        :type error_code: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The corresponding HTTP status code.
        :rtype: int
        '''

        # Retrieve the status code from the service.
        status_code = self.flask_service.get_status_code(
            error_code=error_code
        )

        # Return the status code.
        return status_code
