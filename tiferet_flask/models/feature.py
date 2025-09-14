# *** imports

# ** infra
from tiferet.models.feature import (
    Feature,
    IntegerType
)

# *** models

# ** model: flask_feature
class FlaskFeature(Feature):
    '''
    A feature model for Flask applications.
    '''

    # * attribute: status_code
    status_code = IntegerType(
        required=True,
        default=200,
        metadata=dict(
            description='The default HTTP status code for the feature responses.'
        )
    )