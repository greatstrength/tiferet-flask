# *** imports

# ** core
from typing import List, Any

# ** infra
from tiferet import (
    TiferetError, 
    RaiseError,
    YamlFileProxy
)

# ** app
from ...contracts import (
    FlaskApiRepository,
    FlaskBlueprintContract,
    FlaskRouteContract
)
from ...data import (
    FlaskBlueprintYamlData,
)

# *** proxies

# ** proxy: flask_yaml_proxy
class FlaskYamlProxy(FlaskApiRepository, YamlFileProxy):
    '''
    A YAML configuration proxy for Flask settings.
    '''

    # * init
    def __init__(self, flask_config_file: str):
        '''
        Initialize the FlaskYamlProxy with the given YAML file path.

        :param flask_config_file: The path to the Flask configuration YAML file.
        :type flask_config_file: str
        '''

        # Set the configuration file within the base class.
        super().__init__(flask_config_file)

    # * method: load_yaml
    def load_yaml(self, start_node: callable = lambda data: data, create_data: callable = lambda data: data) -> Any:
        '''
        Load data from the YAML configuration file.
        :param start_node: The starting node in the YAML file.
        :type start_node: str
        :param create_data: A callable to create data objects from the loaded data.
        :type create_data: callable
        :return: The loaded data.
        :rtype: Any
        '''

        # Load the YAML file contents using the yaml config proxy.
        try:
            return super().load_yaml(
                start_node=start_node,
                data_factory=create_data
            )

        # Raise an error if the loading fails.
        except (Exception, TiferetError) as e:
            RaiseError.execute(
                'FLASK_CONFIG_LOADING_FAILED',
                f'Unable to load flask configuration file {self.yaml_file}: {e}.',
                config_file=self.yaml_file,
                e=str(e)
            )

    # * method: get_blueprints
    def get_blueprints(self) -> List[FlaskBlueprintContract]:
        '''
        Retrieve all Flask blueprints from the YAML configuration.

        :return: A list of FlaskBlueprintContract instances.
        :rtype: List[FlaskBlueprintContract]
        '''

        # Load the blueprints section from the YAML file.
        data = self.load_yaml(
            create_data=lambda data: [FlaskBlueprintYamlData.from_data(
                name=name,
                **blueprint
            ) for name, blueprint in data.items()],
            start_node=lambda d: d.get('flask', {}).get('blueprints', {})
        )

        # Map the loaded data to FlaskBlueprintContract instances.
        return [blueprint.map() for blueprint in data]

    # * method: get_route
    def get_route(self, route_id: str, blueprint_name: str = None) -> FlaskRouteContract:
        '''
        Retrieve a specific Flask route by its blueprint and route IDs from the YAML configuration.

        :param route_id: The route identifier.
        :type route_id: str
        :param blueprint_name: The name of the blueprint (optional).
        :type blueprint_name: str
        :return: The corresponding FlaskRouteContract instance.
        :rtype: FlaskRouteContract
        '''

        # Load the blueprints section from the YAML file.
        blueprints = self.get_blueprints()

        # Search for the specified blueprint.
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
        Retrieve the HTTP status code for a given error code from the YAML configuration.

        :param error_code: The error code identifier.
        :type error_code: str
        :return: The corresponding HTTP status code.
        :rtype: int
        '''

        # Load the error code from the errors section of the YAML file.
        data = self.load_yaml(
            start_node=lambda d: d.get('flask').get('errors', {}),
        )

        # Return the status code if found, otherwise default to 500.
        return data.get(error_code, 500)