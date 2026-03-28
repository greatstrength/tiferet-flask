# *** imports

# ** core
from typing import List

# ** infra
from tiferet import (
    Yaml,
    TransferObject
)

# ** app
from ..interfaces import FlaskApiService
from ..mappers import (
    FlaskBlueprintAggregate,
    FlaskRouteAggregate,
    FlaskBlueprintYamlObject,
    FlaskRouteYamlObject
)

# *** repos

# ** repo: flask_yaml_repository
class FlaskYamlRepository(FlaskApiService):
    '''
    A YAML-backed repository for Flask API configuration.
    '''

    # * attribute: yaml_file
    yaml_file: str

    # * attribute: encoding
    encoding: str

    # * attribute: default_role
    default_role: str

    # * init
    def __init__(self, flask_config_file: str, encoding: str = 'utf-8') -> None:
        '''
        Initialize the Flask YAML repository.

        :param flask_config_file: The path to the Flask configuration YAML file.
        :type flask_config_file: str
        :param encoding: The file encoding (default is 'utf-8').
        :type encoding: str
        '''

        # Set the repository attributes.
        self.yaml_file = flask_config_file
        self.encoding = encoding
        self.default_role = 'to_data'

    # * method: exists
    def exists(self, blueprint_name: str) -> bool:
        '''
        Check if a blueprint exists by name.

        :param blueprint_name: The blueprint name.
        :type blueprint_name: str
        :return: True if the blueprint exists, otherwise False.
        :rtype: bool
        '''

        # Load the blueprints mapping from the configuration file.
        blueprints_data = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load(
            start_node=lambda data: data.get('flask', {}).get('blueprints', {})
        )

        # Return whether the blueprint name exists in the mapping.
        return blueprint_name in blueprints_data

    # * method: get_blueprints
    def get_blueprints(self) -> List[FlaskBlueprintAggregate]:
        '''
        Retrieve all Flask blueprints.

        :return: A list of Flask blueprint aggregates.
        :rtype: List[FlaskBlueprintAggregate]
        '''

        # Load the blueprints section from the configuration file.
        blueprints_data = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load(
            start_node=lambda data: data.get('flask', {}).get('blueprints', {})
        )

        # Map each blueprint entry to a FlaskBlueprintAggregate.
        return [
            FlaskBlueprintYamlObject.from_data(
                name=name,
                **blueprint_data
            ).map()
            for name, blueprint_data in blueprints_data.items()
        ]

    # * method: get_route
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

        # Load all blueprints.
        blueprints = self.get_blueprints()

        # Search for the route across blueprints.
        for blueprint in blueprints:
            if blueprint_name and blueprint.name != blueprint_name:
                continue

            # Search for the route within the blueprint.
            for route in blueprint.routes:
                if route.id == route_id:
                    return route

        # If not found, return None.
        return None

    # * method: get_status_code
    def get_status_code(self, error_code: str) -> int:
        '''
        Retrieve the HTTP status code for a given error code.

        :param error_code: The error code identifier.
        :type error_code: str
        :return: The corresponding HTTP status code (defaults to 500).
        :rtype: int
        '''

        # Load the error code mapping from the configuration file.
        errors_data = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load(
            start_node=lambda data: data.get('flask', {}).get('errors', {})
        )

        # Return the status code if found, otherwise default to 500.
        return errors_data.get(error_code, 500)

    # * method: save
    def save(self, blueprint: FlaskBlueprintAggregate) -> None:
        '''
        Save or update a Flask blueprint configuration.

        :param blueprint: The blueprint aggregate to save.
        :type blueprint: FlaskBlueprintAggregate
        :return: None
        :rtype: None
        '''

        # Convert the blueprint aggregate to YAML transfer object.
        blueprint_data = FlaskBlueprintYamlObject.from_model(blueprint)

        # Load the full configuration file.
        full_data = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load()

        # Update or insert the blueprint entry.
        full_data.setdefault('flask', {}).setdefault('blueprints', {})[blueprint.name] = blueprint_data.to_primitive(self.default_role)

        # Persist the updated configuration file.
        Yaml(
            self.yaml_file,
            mode='w',
            encoding=self.encoding,
        ).save(data=full_data)

    # * method: delete
    def delete(self, blueprint_name: str) -> None:
        '''
        Delete a Flask blueprint by name. This operation is idempotent.

        :param blueprint_name: The blueprint name.
        :type blueprint_name: str
        :return: None
        :rtype: None
        '''

        # Load the full configuration file.
        full_data = Yaml(
            self.yaml_file,
            encoding=self.encoding,
        ).load()

        # Remove the blueprint entry if it exists (idempotent).
        full_data.get('flask', {}).get('blueprints', {}).pop(blueprint_name, None)

        # Persist the updated configuration file.
        Yaml(
            self.yaml_file,
            mode='w',
            encoding=self.encoding,
        ).save(data=full_data)
