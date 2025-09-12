# *** imports

# ** core
from typing import List, Any

# ** infra
from tiferet.proxies.yaml import YamlConfigurationProxy, TiferetError, raise_error

# ** app
from ...data.flask import (
    FlaskBlueprintYamlData,
    FlaskBlueprintContract
)
from ...contracts.flask import (
    FlaskApiRepository
)

# *** proxies

# ** proxy: flask_yaml_proxy
class FlaskYamlProxy(FlaskApiRepository, YamlConfigurationProxy):
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
                create_data=create_data
            )
        
        # Raise an error if the loading fails.
        except (Exception, TiferetError) as e:
            raise_error.execute(
                'FLASK_CONFIG_LOADING_FAILED',
                f'Unable to load flask configuration file {self.config_file}: {e}.',
                self.config_file,
                str(e)
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
                id=id,
                **blueprint
            ) for blueprint in data.items()],
            start_node=lambda d: d.get('flask', {}).get('blueprints', {})
        )

        # Map the loaded data to FlaskBlueprintContract instances.
        return [blueprint.map() for blueprint in data]