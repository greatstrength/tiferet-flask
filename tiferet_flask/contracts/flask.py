# *** imports

# ** core
from typing import List
from abc import abstractmethod

# ** infra
from tiferet import (
    ModelContract,
    Repository,
)

# *** contracts

# ** contract: flask_route_contract
class FlaskRouteContract(ModelContract):
    '''
    A contract for Flask route models.
    '''

    # * attribute: id
    id: str

    # * attribute: status_code
    status_code: int

# ** contract: flask_blueprint_contract
class FlaskBlueprintContract(ModelContract):
    '''
    A contract for Flask blueprint models.
    '''

    # * attribute: name
    name: str

    # * attribute: routes
    routes: List[FlaskRouteContract]

# ** contract: flask_api_repository
class FlaskApiRepository(Repository):
    '''
    A repository contract for managing Flask API entities.
    '''

    # * method: get_blueprints
    @abstractmethod
    def get_blueprints(self) -> List[FlaskBlueprintContract]:
        '''
        Retrieve all Flask blueprints.

        :return: A list of FlaskBlueprintContract instances.
        :rtype: List[FlaskBlueprintContract]
        '''
        raise NotImplementedError('get_blueprints method not implemented.')

    # * method: get_route
    @abstractmethod
    def get_route(self, route_id: str, blueprint_name: str = None) -> FlaskRouteContract:
        '''
        Retrieve a specific Flask route by its blueprint and route IDs.

        :param route_id: The ID of the route within the blueprint.
        :type route_id: str
        :param blueprint_name: The name of the blueprint (optional).
        :type blueprint_name: str
        :return: The corresponding FlaskRouteContract instance.
        :rtype: FlaskRouteContract
        '''
        raise NotImplementedError('get_route method not implemented.')

    # * method: get_status_code
    @abstractmethod
    def get_status_code(self, error_code: str) -> int:
        '''
        Retrieve the HTTP status code for a given error code.

        :param error_code: The error code.
        :type error_code: str
        :return: The corresponding HTTP status code.
        :rtype: int
        '''
        raise NotImplementedError('get_status_code method not implemented.')