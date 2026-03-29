# FlaskBlueprint

**Package:** `tiferet_flask.domain.flask`
**Base Class:** `DomainObject`

## Description

Represents a Flask blueprint containing a collection of routes. A `FlaskBlueprint` groups related API endpoints under a common name and optional URL prefix.

## Attributes

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | `StringType` | Yes | — | The name of the blueprint. |
| `url_prefix` | `StringType` | No | `None` | The URL prefix for all routes in this blueprint. |
| `routes` | `ListType(ModelType(FlaskRoute))` | No | `[]` | A list of routes associated with this blueprint. |

## Instantiation

```python
from tiferet import DomainObject
from tiferet_flask.domain import FlaskBlueprint, FlaskRoute

blueprint = DomainObject.new(
    FlaskBlueprint,
    name='calc',
    url_prefix='/calc',
    routes=[
        DomainObject.new(FlaskRoute, id='add', rule='/add', methods=['POST'])
    ]
)
```

## Usage

`FlaskBlueprint` instances are consumed by `FlaskApiContext.build_flask_app()` to assemble the Flask application. The context iterates over blueprints returned by `get_blueprints_handler()`, builds each into a Flask `Blueprint`, and registers it with the Flask app.

## See Also

- [FlaskRoute](flask_route.md)
- `tiferet_flask/mappers/flask.py` — `FlaskBlueprintAggregate`, `FlaskBlueprintYamlObject`
