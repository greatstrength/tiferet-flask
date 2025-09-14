# *** imports

# ** core
from typing import List

# ** infra
from tiferet.contracts import (
    ModelContract,
    Repository,
    abstractmethod
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
    
    # * attribute: id
    id: str

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
    def get_route(self, route_id: str, blueprint_id: str = None) -> FlaskRouteContract:
        '''
        Retrieve a specific Flask route by its blueprint and route IDs.

        :param route_id: The ID of the route within the blueprint.
        :type route_id: str
        :param blueprint_id: The ID of the blueprint (optional).
        :type blueprint_id: str
        :return: The corresponding FlaskRouteContract instance.
        :rtype: FlaskRouteContract
        '''
        raise NotImplementedError('get_route method not implemented.')