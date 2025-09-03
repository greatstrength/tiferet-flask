# *** imports

# ** core
from typing import List

# ** infra
from tiferet.contracts import *

# *** contracts

# ** contract: flask_route_contract
class FlaskRouteContract(ModelContract):
    '''
    A contract for Flask route models.
    '''

    # * attribute
    id: str
    
    # * attribute
    rule: str

    # * attribute
    methods: List[str]

# ** contract: flask_blueprint_contract
class FlaskBlueprintContract(ModelContract):
    '''
    A contract for Flask blueprint models.
    '''

    # * attribute
    id: str

    # * attribute
    name: str

    # * attribute
    url_prefix: str

    # * attribute
    routes: List[FlaskRouteContract]

# ** contract: flask_api_repository
class FlaskAPIRepository(Repository):
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