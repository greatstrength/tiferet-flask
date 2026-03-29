# GetFlaskStatusCode

**Package:** `tiferet_flask.events.flask`
**Base Class:** `DomainEvent`

## Description

Retrieves the HTTP status code mapped to a given error code. Used by `FlaskApiContext.handle_error()` to determine the appropriate HTTP response status for Tiferet errors.

## Dependencies

| Attribute | Type | Description |
|-----------|------|-------------|
| `flask_service` | `FlaskApiService` | The Flask API service for configuration access. |

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `error_code` | `str` | Yes | The error code identifier (e.g., `DIVIDE_BY_ZERO`). |

Validated via `@DomainEvent.parameters_required(['error_code'])`.

## Returns

`int` — The corresponding HTTP status code. Defaults to `500` for unknown error codes.

## Test Invocation

```python
from tiferet.events import DomainEvent
from tiferet_flask.events import GetFlaskStatusCode

result = DomainEvent.handle(
    GetFlaskStatusCode,
    dependencies={'flask_service': mock_flask_service},
    error_code='DIVIDE_BY_ZERO',
)
```

## See Also

- [GetFlaskBlueprints](get_flask_blueprints.md)
- [GetFlaskRoute](get_flask_route.md)
