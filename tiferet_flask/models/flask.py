# *** imports

# ** infra
from tiferet.models import (
    ModelObject,
    StringType,
    IntegerType,
    ListType,
    ModelType
)

# *** models

# ** model: flask_route
class FlaskRoute(ModelObject):
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

    # * attribute: status_code
    status_code = IntegerType(
        default=200,
        metadata=dict(
            description='The default HTTP status code for the route response.'
        )
    )

# ** model: flask_blueprint
class FlaskBlueprint(ModelObject):
    '''
    A Flask blueprint model.
    '''

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

    # * attribute: routes
    routes = ListType(
        ModelType(FlaskRoute),
        default=[],
        metadata=dict(
            description='A list of routes associated with this blueprint.'
        )
    )