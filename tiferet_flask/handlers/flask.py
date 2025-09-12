# *** imports

# ** core
from typing import List

# ** app
from ..contracts.flask import (
    FlaskBlueprintContract,
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