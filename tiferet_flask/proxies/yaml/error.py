# *** imports

# ** core
from typing import List

# ** infra
from tiferet.proxies.yaml.error import ErrorYamlProxy
from tiferet.data import DataObject
from tiferet.contracts.error import Error as ErrorContract

# ** app
from ...data.error import (
    FlaskErrorYamlData,
)

# *** proxies
# ** proxy: flask_error_yaml_proxy
class FlaskErrorYamlProxy(ErrorYamlProxy):
    '''
    A YAML configuration proxy for Flask error settings.
    '''

        # * method: get
    def get(self, id: str) -> ErrorContract:
        '''
        Get the error.
        
        :param id: The error id.
        :type id: str
        :return: The error.
        :rtype: Error
        '''

        # Load the error data from the yaml configuration file.
        data: DataObject = self.load_yaml(
            create_data=lambda data: DataObject.from_data(
                FlaskErrorYamlData,
                id=id, 
                **data
            ),
            start_node=lambda data: data.get('errors').get(id))

        # Return the error object.
        return data.map() if data else None
    
    # * method: list
    def list(self) -> List[ErrorContract]:
        '''
        List all errors.

        :return: The list of errors.
        :rtype: List[Error]
        '''

        # Load the error data from the yaml configuration file.
        data: List[FlaskErrorYamlData] = self.load_yaml(
            create_data=lambda data: [DataObject.from_data(
                FlaskErrorYamlData,
                id=id, 
                **error_data) 
                for id, error_data in data.items()
            ],
            start_node=lambda data: data.get('errors'))

        # Return the error object.
        return [obj.map() for obj in data]