# *** imports

# ** core
from typing import List

# ** infra
from tiferet import RaiseError

# ** app
from ..contracts import (
    FlaskBlueprintContract,
    FlaskRouteContract,
    FlaskApiRepository
)

# *** handlers

# ** handler: flask_api_handler
class FlaskApiHandler(object):
    '''
    A handler for managing Flask API entities.
    '''

    # * init
    def __init__(self, flask_repo: FlaskApiRepository):
        '''
        Initialize the FlaskHandler with the given repository.

        :param flask_repo: An instance of FlaskApiRepository.
        :type flask_repo: FlaskApiRepository
        '''

        # Store the repository instance.
        self.flask_repo = flask_repo

    # * method: get_blueprints
    def get_blueprints(self) -> List[FlaskBlueprintContract]:
        '''
        Retrieve all Flask blueprints using the repository.

        :return: A list of FlaskBlueprintContract instances.
        :rtype: List[FlaskBlueprintContract]
        '''

        # Delegate the call to the repository.
        return self.flask_repo.get_blueprints()

    # * method: get_route
    def get_route(self, endpoint: str) -> FlaskRouteContract:
        '''
        Retrieve a specific Flask route by its blueprint and route IDs.

        :param endpoint: The endpoint in the format 'blueprint_name.route_id'.
        :type endpoint: str
        :return: The corresponding FlaskRouteContract instance.
        :rtype: FlaskRouteContract
        '''

        # Split the endpoint into blueprint and route IDs.
        # If no blueprint is specified, assume the route is at the root level.
        blueprint_name = None
        try:
            blueprint_name, route_id = endpoint.split('.')
        except ValueError:
            route_id = endpoint

        # Delegate the call to the repository.
        route = self.flask_repo.get_route(
            route_id=route_id,
            blueprint_name=blueprint_name,
        )

        # Raise an error if the route is not found.
        if route is None:
            RaiseError.execute(
                'FLASK_ROUTE_NOT_FOUND',
                f'Flask route not found for endpoint: {endpoint}',
                endpoint=endpoint
            )

        # Return the found route.
        return route

    # * method: get_status_code
    def get_status_code(self, error_code: str) -> int:
        '''
        Retrieve the HTTP status code for a given error code using the repository.

        :param error_code: The error code identifier.
        :type error_code: str
        :return: The corresponding HTTP status code.
        :rtype: int
        '''

        # Delegate the call to the repository.
        return self.flask_repo.get_status_code(
            error_code=error_code
        )