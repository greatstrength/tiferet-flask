# *** imports

# ** infra
from tiferet.models import *


# *** models

# ** model: flask_route
class FlaskRoute(Entity):
    '''
    A Flask route model.
    '''

    # * attribute: id
    id = StringType(
        required=True,
        metadata=dict(
            description='The unique identifier of the route endpoint.'
        )
    )

    # * attribute: rule
    rule = StringType(
        required=True,
        metadata=dict(
            description='The URL rule as string.'
        )
    )

    # * attribute: methods
    methods = ListType(
        StringType,
        required=True,
        metadata=dict(
            description='A list of HTTP methods this rule should be limited to.'
        )
    )

# ** model: flask_blueprint
class FlaskBlueprint(Entity):
    '''
    A Flask blueprint model.
    '''

    # * attribute: id
    id = StringType(
        required=True,
        metadata=dict(
            description='The unique identifier of the blueprint.'
        )
    )

    # * attribute: name
    name = StringType(
        required=True,
        metadata=dict(
            description='The name of the blueprint.'
        )
    )

    # * attribute: url_prefix
    url_prefix = StringType(
        metadata=dict(
            description='The URL prefix for all routes in this blueprint.'
        )
    )