# *** imports

# ** core
from abc import abstractmethod
from typing import List

# ** infra
from tiferet.interfaces.settings import Service

# ** app
from ..mappers import (
    FlaskBlueprintAggregate,
    FlaskRouteAggregate
)

# *** interfaces

# ** interface: flask_api_service
class FlaskApiService(Service):
    '''
    Service interface for managing Flask API configuration.
    '''

    # * method: exists
    @abstractmethod
    def exists(self, blueprint_name: str) -> bool:
        '''
        Check if a blueprint exists by name.

        :param blueprint_name: The blueprint name.
        :type blueprint_name: str
        :return: True if the blueprint exists, otherwise False.
        :rtype: bool
        '''
        raise NotImplementedError('exists method is required for FlaskApiService.')

    # * method: get_blueprints
    @abstractmethod
    def get_blueprints(self) -> List[FlaskBlueprintAggregate]:
        '''
        Retrieve all Flask blueprints.

        :return: A list of Flask blueprint aggregates.
        :rtype: List[FlaskBlueprintAggregate]
        '''
        raise NotImplementedError('get_blueprints method is required for FlaskApiService.')

    # * method: get_route
    @abstractmethod
    def get_route(self, route_id: str, blueprint_name: str = None) -> FlaskRouteAggregate | None:
        '''
        Retrieve a specific Flask route by its ID and optional blueprint name.

        :param route_id: The route identifier.
        :type route_id: str
        :param blueprint_name: The blueprint name (optional).
        :type blueprint_name: str
        :return: The Flask route aggregate, or None if not found.
        :rtype: FlaskRouteAggregate | None
        '''
        raise NotImplementedError('get_route method is required for FlaskApiService.')

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
        raise NotImplementedError('get_status_code method is required for FlaskApiService.')

    # * method: save
    @abstractmethod
    def save(self, blueprint: FlaskBlueprintAggregate) -> None:
        '''
        Save or update a Flask blueprint configuration.

        :param blueprint: The blueprint aggregate to save.
        :type blueprint: FlaskBlueprintAggregate
        :return: None
        :rtype: None
        '''
        raise NotImplementedError('save method is required for FlaskApiService.')

    # * method: delete
    @abstractmethod
    def delete(self, blueprint_name: str) -> None:
        '''
        Delete a Flask blueprint by name. This operation should be idempotent.

        :param blueprint_name: The blueprint name.
        :type blueprint_name: str
        :return: None
        :rtype: None
        '''
        raise NotImplementedError('delete method is required for FlaskApiService.')
