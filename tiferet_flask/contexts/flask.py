'''Flask API context.'''

# *** imports

# ** infra
from tiferet_openapi import OpenApiContext


# *** contexts

# ** context: flask_api_context
class FlaskApiContext(OpenApiContext):
    '''
    A Flask-specific API context extending the shared OpenAPI context.
    '''
    pass
