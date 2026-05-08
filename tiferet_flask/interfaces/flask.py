"""Flask service interfaces."""

# *** imports

# ** core
from abc import abstractmethod
from typing import List

# ** infra
from tiferet.interfaces import Service

# ** app
from ..domain import FlaskBlueprint, FlaskRoute

# *** interfaces

# ** interface: flask_api_service
class FlaskApiService(Service):
    '''
    Service interface for managing Flask API configuration.
    '''

    # * method: get_blueprints
    @abstractmethod
    def get_blueprints(self) -> List[FlaskBlueprint]:
        '''
        Retrieve all Flask blueprints.

        :return: A list of Flask blueprints.
        :rtype: List[FlaskBlueprint]
        '''
        raise NotImplementedError()

    # * method: get_route
    @abstractmethod
    def get_route(self, route_id: str, blueprint_name: str = None) -> FlaskRoute:
        '''
        Retrieve a specific Flask route by its ID and optional blueprint name.

        :param route_id: The route identifier.
        :type route_id: str
        :param blueprint_name: The blueprint name (optional).
        :type blueprint_name: str
        :return: The Flask route.
        :rtype: FlaskRoute
        '''
        raise NotImplementedError()

    # * method: get_status_code
    @abstractmethod
    def get_status_code(self, error_code: str) -> int:
        '''
        Retrieve the HTTP status code for a given error code.

        :param error_code: The error code identifier.
        :type error_code: str
        :return: The corresponding HTTP status code.
        :rtype: int
        '''
        raise NotImplementedError()
