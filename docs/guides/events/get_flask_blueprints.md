# GetFlaskBlueprints

**Package:** `tiferet_flask.events.flask`
**Base Class:** `DomainEvent`

## Description

Retrieves all Flask blueprints from the `FlaskApiService`. This event is used by `FlaskApiContext` during application startup to load blueprint configurations for route registration.

## Dependencies

| Attribute | Type | Description |
|-----------|------|-------------|
| `flask_service` | `FlaskApiService` | The Flask API service for configuration access. |

## Parameters

None required.

## Returns

`List[FlaskBlueprintAggregate]` — A list of all Flask blueprint aggregates.

## Test Invocation

```python
from tiferet.events import DomainEvent
from tiferet_flask.events import GetFlaskBlueprints

result = DomainEvent.handle(
    GetFlaskBlueprints,
    dependencies={'flask_service': mock_flask_service},
)
```

## See Also

- [GetFlaskRoute](get_flask_route.md)
- [GetFlaskStatusCode](get_flask_status_code.md)
- `tiferet_flask/interfaces/flask.py` — `FlaskApiService`
