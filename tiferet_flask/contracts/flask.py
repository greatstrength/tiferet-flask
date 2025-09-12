# *** imports

# ** core
from typing import List

# ** infra
from tiferet.contracts import (
    ModelContract,
    Repository
)

# *** contracts

# ** contract: flask_route_contract
class FlaskRouteContract(ModelContract):
    '''
    A contract for Flask route models.
    '''
    pass

# ** contract: flask_blueprint_contract
class FlaskBlueprintContract(ModelContract):
    '''
    A contract for Flask blueprint models.
    '''
    pass

# ** contract: flask_api_repository
class FlaskApiRepository(Repository):
    '''
    A repository contract for managing Flask API entities.
    '''

    # * method: get_blueprints
    def get_blueprints(self) -> List[FlaskBlueprintContract]:
        '''
        Retrieve all Flask blueprints.

        :return: A list of FlaskBlueprintContract instances.
        :rtype: List[FlaskBlueprintContract]
        '''
        raise NotImplementedError