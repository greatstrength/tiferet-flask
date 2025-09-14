# *** imports

# ** core
from typing import List

# ** app
from ..contracts.flask import (
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

        :param endpoint: The endpoint in the format 'blueprint_id.route_id'.
        :type endpoint: str
        :return: The corresponding FlaskRouteContract instance.
        :rtype: FlaskRouteContract
        '''

        # Split the endpoint into blueprint and route IDs.
        # If no blueprint is specified, assume the route is at the root level.
        blueprint_id = None
        try:
            blueprint_id, route_id = endpoint.split('.')
        except ValueError:
            route_id = endpoint

        # Delegate the call to the repository.
        return self.flask_repo.get_route(
            route_id=route_id,
            blueprint_id=blueprint_id,
        )