"""Flask YAML repository."""

# *** imports

# ** core
from typing import List

# ** infra
from tiferet.utils import YamlLoader

# ** app
from ..domain import FlaskBlueprint, FlaskRoute
from ..interfaces import FlaskApiService
from ..mappers import FlaskBlueprintYamlObject

# *** repos

# ** repo: flask_yaml_repository
class FlaskYamlRepository(FlaskApiService):
    '''
    A YAML-backed repository for Flask API configuration.
    '''

    # * attribute: flask_yaml_file
    flask_yaml_file: str

    # * attribute: encoding
    encoding: str

    # * init
    def __init__(self, flask_yaml_file: str, encoding: str = 'utf-8'):
        '''
        Initialize the Flask YAML repository.

        :param flask_yaml_file: The path to the Flask configuration YAML file.
        :type flask_yaml_file: str
        :param encoding: The file encoding.
        :type encoding: str
        '''

        # Set the YAML file path and encoding.
        self.flask_yaml_file = flask_yaml_file
        self.encoding = encoding

    # * method: get_blueprints
    def get_blueprints(self) -> List[FlaskBlueprint]:
        '''
        Retrieve all Flask blueprints.

        :return: A list of Flask blueprints.
        :rtype: List[FlaskBlueprint]
        '''

        # Load the blueprints section from the YAML file.
        loader = YamlLoader(path=self.flask_yaml_file, mode='r', encoding=self.encoding)
        data = loader.load(
            start_node=lambda d: d.get('flask', {}).get('blueprints', {}),
        )

        # Map each blueprint entry to a domain object via FlaskBlueprintYamlObject.
        return [
            FlaskBlueprintYamlObject.model_validate(dict(name=name, **bp_data)).map()
            for name, bp_data in data.items()
        ]

    # * method: get_route
    def get_route(self, route_id: str, blueprint_name: str = None) -> FlaskRoute:
        '''
        Retrieve a specific Flask route by its ID and optional blueprint name.

        :param route_id: The route identifier.
        :type route_id: str
        :param blueprint_name: The blueprint name (optional).
        :type blueprint_name: str
        :return: The corresponding FlaskRoute instance, or None if not found.
        :rtype: FlaskRoute
        '''

        # Load all blueprints.
        blueprints = self.get_blueprints()

        # Search for the route across blueprints.
        for blueprint in blueprints:
            if blueprint_name and blueprint.name != blueprint_name:
                continue
            for route in blueprint.routes:
                if route.id == route_id:
                    return route

        # Return None if not found.
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

        # Load the errors section from the YAML file.
        loader = YamlLoader(path=self.flask_yaml_file, mode='r', encoding=self.encoding)
        data = loader.load(
            start_node=lambda d: d.get('flask', {}).get('errors', {}),
        )

        # Return the status code if found, otherwise default to 500.
        return data.get(error_code, 500)
