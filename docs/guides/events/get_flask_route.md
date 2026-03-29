# GetFlaskRoute

**Package:** `tiferet_flask.events.flask`
**Base Class:** `DomainEvent`

## Description

Retrieves a Flask route by its endpoint string. The endpoint is parsed to extract an optional blueprint name and route ID. If the route is not found, a `FLASK_ROUTE_NOT_FOUND` error is raised.

## Dependencies

| Attribute | Type | Description |
|-----------|------|-------------|
| `flask_service` | `FlaskApiService` | The Flask API service for configuration access. |

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `endpoint` | `str` | Yes | The endpoint identifier in format `blueprint_name.route_id` or just `route_id`. |

Validated via `@DomainEvent.parameters_required(['endpoint'])`.

## Behavior

1. Parses the endpoint string — splits on `.` to extract `blueprint_name` and `route_id`. Falls back to `route_id` only if no `.` is present.
2. Delegates to `flask_service.get_route(route_id, blueprint_name)`.
3. Verifies the route exists via `self.verify()`. Raises `FLASK_ROUTE_NOT_FOUND` if `None`.

## Returns

`FlaskRouteAggregate` — The matching Flask route aggregate.

## Errors

| Error Code | Condition |
|------------|-----------|
| `FLASK_ROUTE_NOT_FOUND` | Route does not exist for the given endpoint. |

## Test Invocation

```python
from tiferet.events import DomainEvent
from tiferet_flask.events import GetFlaskRoute

result = DomainEvent.handle(
    GetFlaskRoute,
    dependencies={'flask_service': mock_flask_service},
    endpoint='calc.add',
)
```

## See Also

- [GetFlaskBlueprints](get_flask_blueprints.md)
- [GetFlaskStatusCode](get_flask_status_code.md)
