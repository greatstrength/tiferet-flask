"""Flask domain models."""

# *** imports

# ** core
from typing import List

# ** infra
from pydantic import Field

# ** app
from tiferet.domain import DomainObject

# *** models

# ** model: flask_route
class FlaskRoute(DomainObject):
    '''
    A Flask route domain object.
    '''

    # * attribute: id
    id: str = Field(
        ...,
        description='The unique identifier of the route.',
    )

    # * attribute: endpoint
    endpoint: str = Field(
        ...,
        description='The fully-qualified endpoint (blueprint_name.route_id).',
    )

    # * attribute: rule
    rule: str = Field(
        ...,
        description='The URL rule as string.',
    )

    # * attribute: methods
    methods: List[str] = Field(
        ...,
        description='HTTP methods this rule is limited to.',
    )

    # * attribute: status_code
    status_code: int = Field(
        default=200,
        description='The default HTTP status code for the route response.',
    )

# ** model: flask_blueprint
class FlaskBlueprint(DomainObject):
    '''
    A Flask blueprint domain object.
    '''

    # * attribute: name
    name: str = Field(
        ...,
        description='The name of the blueprint.',
    )

    # * attribute: url_prefix
    url_prefix: str | None = Field(
        default=None,
        description='The URL prefix for all routes in this blueprint.',
    )

    # * attribute: routes
    routes: List[FlaskRoute] = Field(
        default_factory=list,
        description='A list of routes associated with this blueprint.',
    )
