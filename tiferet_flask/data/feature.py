# *** imports

# ** infra
from tiferet.models import ModelObject
from tiferet.data.feature import (
    DataObject,
    FeatureData as FeatureYamlData
)
from tiferet.contracts.feature import (
    Feature as FeatureContract
)

# ** app
from ..models.feature import (
    FlaskFeature
)

# *** data

# ** data: flask_feature_yaml_data
class FlaskFeatureYamlData(FeatureYamlData, FlaskFeature):
    '''
    A data object for Flask feature model from YAML.
    '''

    class Options():
        serialize_when_none = False
        roles = {
            'to_model': DataObject.deny('commands'),
        }
    
    # * method: map
    def map(self, role: str = 'to_model', **kwargs) -> FeatureContract:
        '''
        Map the data object to a FlaskFeature instance.

        :return: A FlaskFeature instance.
        :rtype: FlaskFeature
        '''

        # Map the data object to a model instance.
        return ModelObject.new(
            FlaskFeature,
            **self.to_primitive(role),
            commands=[command.map(role, **kwargs) for command in self.commands],
            **kwargs
        )