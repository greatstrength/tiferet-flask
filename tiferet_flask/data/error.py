# *** imports

# ** infra
from tiferet.data.error import (
    ModelObject,
    ErrorData as ErrorYamlData
)
from tiferet.contracts.error import (
    Error as ErrorContract
)

# ** app
from ..models.error import (
    FlaskError
)

# *** data

# ** data: flask_error_yaml_data
class FlaskErrorYamlData(ErrorYamlData, FlaskError):
    '''
    A data object for Flask error model from YAML.
    '''
    
    # * method: map
    def map(self, role: str = 'to_model') -> ErrorContract:
        '''
        Map the data object to a FlaskError instance.

        :param role: The role for primitive conversion.
        :type role: str
        :return: A FlaskError instance.
        :rtype: FlaskError
        '''

        # Map the data object to a model instance.
        return ModelObject.new(
            FlaskError,
            **self.to_primitive(role)
        )