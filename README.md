# Tiferet Flask - A Flask Extension for the Tiferet Framework

## Introduction

Tiferet Flask extends the [Tiferet](https://github.com/greatstrength/tiferet) Python framework to build Flask-based APIs using Domain-Driven Design (DDD). It uses [tiferet-openapi](https://github.com/greatstrength/tiferet-openapi) as its domain backbone, providing a thin Flask integration layer on top of the shared OpenAPI abstraction.

**Key components:**
- `build_flask_app` / `FlaskApp` — assembles a Flask app from `ApiRouter`/`ApiRoute` domain objects using blueprint functions.
- `FlaskApiContext` — extends `OpenApiContext` with Swagger UI support.
- `FlaskRequestContext` — alias for `OpenApiRequestContext` with Pydantic serialization.

## Getting Started

### Prerequisites

- Python 3.10+
- A virtual environment (recommended)

### Installation

```bash
pip install tiferet-flask
```

This installs `tiferet-openapi` (which transitively provides `tiferet`) along with Flask and Flask-CORS.

### Project Structure

```plaintext
project_root/
├── calc_flask_api.py
└── app/
    ├── events/
    │   ├── __init__.py
    │   └── calc.py
    └── configs/
        ├── app.yml
        ├── openapi.yml
        ├── container.yml
        ├── error.yml
        └── feature.yml
```

## Configuration

### App Interface (`app/configs/app.yml`)

Define the Flask API interface using tiferet-openapi types:

```yaml
interfaces:
  calc_flask_api:
    name: Calculator Flask API
    description: Arithmetic operations via Flask API
    module_path: tiferet_flask.contexts.flask
    class_name: FlaskApiContext
    attrs:
      get_routers_evt:
        module_path: tiferet_openapi.events.openapi
        class_name: GetRouters
      get_route_evt:
        module_path: tiferet_openapi.events.openapi
        class_name: GetRoute
      get_status_code_evt:
        module_path: tiferet_openapi.events.openapi
        class_name: GetStatusCode
      openapi_service:
        module_path: tiferet_openapi.repos.openapi
        class_name: OpenApiYamlRepository
        params:
          openapi_yaml_file: app/configs/openapi.yml
```

### OpenAPI Configuration (`app/configs/openapi.yml`)

Define routers, routes, and error status codes using the `openapi:` root key:

```yaml
openapi:
  routers:
    calc:
      prefix: /calc
      routes:
        add:
          path: /add
          methods: [POST, GET]
          status_code: 200
        subtract:
          path: /subtract
          methods: [POST, GET]
          status_code: 200
        divide:
          path: /divide
          methods: [POST, GET]
          status_code: 200
        sqrt:
          path: /sqrt
          methods: [POST, GET]
          status_code: 200
  errors:
    DIVISION_BY_ZERO: 400
    INVALID_INPUT: 422
```

## Usage

### Entry Point (`calc_flask_api.py`)

```python
from tiferet_flask import FlaskApp

# Define the view function.
def view_func(**kwargs):
    from flask import request, jsonify

    data = dict(request.json) if request.is_json else {}
    data.update(dict(request.args))
    data.update(kwargs)
    headers = dict(request.headers)

    response, status_code = context.run(
        feature_id=request.endpoint,
        headers=headers,
        data=data,
    )
    return jsonify(response), status_code

# Build the Flask app with Swagger UI enabled.
flask_app = FlaskApp('calc_flask_api', view_func, swagger=True)

if __name__ == '__main__':
    flask_app.run(host='127.0.0.1', port=5000, debug=True)
```

### Endpoints

```bash
# Add two numbers
curl -X POST http://127.0.0.1:5000/calc/add \
  -H "Content-Type: application/json" -d '{"a": 1, "b": 2}'
# Output: 3

# Square root
curl -X POST http://127.0.0.1:5000/calc/sqrt \
  -H "Content-Type: application/json" -d '{"a": 16}'
# Output: 4.0

# Division by zero
curl -X POST http://127.0.0.1:5000/calc/divide \
  -H "Content-Type: application/json" -d '{"a": 5, "b": 0}'
# Output: {"error_code": "DIVISION_BY_ZERO", ...}
```

### Swagger UI

When `swagger=True` is passed to `FlaskApp()`, Swagger UI is available at:
- **Swagger UI:** `http://127.0.0.1:5000/docs`
- **OpenAPI spec:** `http://127.0.0.1:5000/docs/openapi.json`

## Architecture

Tiferet Flask v0.5.0 delegates all domain, interface, event, mapper, and repository concerns to `tiferet-openapi`. Only two packages remain under `tiferet_flask/`:

- **`blueprints/`** — Stateless blueprint functions (`build_flask_app`, `build_blueprint`, `get_routers`, `run`) that consume `ApiRouter`/`ApiRoute` from tiferet-openapi, map them to Flask Blueprints, and optionally register a Swagger UI blueprint. Exported as `FlaskApp` alias.
- **`contexts/`** — `FlaskApiContext` is a thin subclass of `OpenApiContext` that adds `create_swagger_blueprint()`. `FlaskRequestContext` is an alias for `OpenApiRequestContext`.

For domain-level documentation (domain objects, events, mappers, repositories), see [tiferet-openapi](https://github.com/greatstrength/tiferet-openapi).

## Migration from v0.4.x

- **Builders → Blueprints:** The `FlaskAppBuilder` class has been replaced by stateless blueprint functions. `FlaskAppBuilder()` → `build_flask_app()` / `FlaskApp()`. No more class instantiation — call the function directly.
- **Imports:** `from tiferet_flask import FlaskAppBuilder` → `from tiferet_flask import FlaskApp` (or `build_flask_app`).
- **Usage:** `builder = FlaskAppBuilder(); builder.run(...)` → `flask_app = FlaskApp(interface_id, view_func, swagger=True)`.
- **Dependencies:** The direct `tiferet>=2.0.0b1` dependency has been removed. Tiferet is now provided transitively through `tiferet-openapi>=0.1.3`.

## Example

See the [`example/`](example/) directory for a complete calculator Flask API demonstrating the v0.5.0 architecture with Swagger support.

## License

MIT
