# *** imports

# ** infra
from tiferet.models import IntegerType
from tiferet.models.error import Error

# *** models

# ** model: flask_error
class FlaskError(Error):
    '''
    A model representing errors specific to Flask API operations.
    '''

    # * attribute: status_code
    status_code = IntegerType(
        required=True,
        metadata=dict(
            description='The HTTP status code associated with the error.'
        )
    )
    