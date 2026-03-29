# FlaskRoute

**Package:** `tiferet_flask.domain.flask`
**Base Class:** `DomainObject`

## Description

Represents a single Flask route endpoint. A `FlaskRoute` defines the URL rule, allowed HTTP methods, and default status code for an API endpoint.

## Attributes

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `id` | `StringType` | Yes | — | The unique identifier of the route endpoint. |
| `rule` | `StringType` | Yes | — | The URL rule as string (e.g., `/sample`). |
| `methods` | `ListType(StringType)` | Yes | — | A list of HTTP methods this rule should be limited to. |
| `status_code` | `IntegerType` | No | `200` | The default HTTP status code for the route response. |

## Instantiation

```python
from tiferet import DomainObject
from tiferet_flask.domain import FlaskRoute

route = DomainObject.new(
    FlaskRoute,
    id='sample_route',
    rule='/sample',
    methods=['GET', 'POST'],
    status_code=200
)
```

## Usage

`FlaskRoute` instances are consumed by `FlaskApiContext.build_blueprint()` to register URL rules on Flask blueprints. They are typically loaded from YAML configuration via `FlaskYamlRepository.get_blueprints()` as part of `FlaskBlueprint.routes`.

## See Also

- [FlaskBlueprint](flask_blueprint.md)
- `tiferet_flask/mappers/flask.py` — `FlaskRouteAggregate`, `FlaskRouteYamlObject`
