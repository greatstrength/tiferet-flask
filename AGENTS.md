# AGENTS.md — Tiferet Flask (v0.5.0)

## Project Overview

**Tiferet Flask** is a Flask extension for the Tiferet framework, providing Flask-specific API assembly and Swagger UI support on top of the shared [tiferet-openapi](https://github.com/greatstrength/tiferet-openapi) abstraction layer. All domain objects, service interfaces, domain events, mappers, and repositories are provided by `tiferet-openapi`.

- **Repository:** https://github.com/greatstrength/tiferet-flask
- **Branch:** `main`
- **Python:** ≥ 3.10
- **Version:** `0.5.0`
- **Dependencies:** `tiferet-openapi >= 0.1.3`, `flask >= 3.1.2`, `flask_cors >= 6.0.1`

## Architecture

### Package Layout

```
tiferet_flask/
├── __init__.py          — Version (0.5.0) and public exports
├── blueprints/          — Stateless blueprint functions (build_flask_app, build_blueprint, get_routers, run)
└── contexts/            — FlaskApiContext (OpenApiContext), FlaskRequestContext (alias)
```

All domain, interface, event, mapper, and repository layers are provided by `tiferet-openapi`. No `domain/`, `interfaces/`, `events/`, `mappers/`, or `repos/` packages exist under `tiferet_flask/`.

### Key Concepts

- **Blueprint functions** (`blueprints/flask.py`): Stateless functions that consume `ApiRouter`/`ApiRoute` from `tiferet_openapi`. Functions: `get_routers(service_provider)`, `build_blueprint(router, view_func)`, `build_flask_app(interface_id, view_func, swagger=False)`, `run(interface_id, view_func)`. `build_flask_app` is exported as the `FlaskApp` alias.
- **FlaskApiContext** (`contexts/flask.py`): Thin subclass of `tiferet_openapi.OpenApiContext`. Inherits `parse_request()`, `handle_error()`, `handle_response()`, `generate_spec()`, `get_routers_handler`. Adds `create_swagger_blueprint(title, version, description)` and overrides `create_docs_handler()` to delegate to it.
- **FlaskRequestContext** (`contexts/request.py`): Alias for `tiferet_openapi.OpenApiRequestContext`. Provides Pydantic `BaseModel.model_dump()` serialization for responses.

### Domain Types (from tiferet-openapi)

- `ApiRoute` — route with `id`, `endpoint`, `path`, `methods`, `status_code`.
- `ApiRouter` — router with `name`, `prefix`, `routes`.
- `OpenApiService` — service interface for route/router/status code access.
- `GetRouters`, `GetRoute`, `GetStatusCode` — domain events.
- `OpenApiYamlRepository` — YAML-backed service implementation.

### Runtime Flow

1. `FlaskApp(interface_id, view_func, swagger=True)` (alias for `build_flask_app`) resolves the interface definition via `tiferet.blueprints.main`.
2. Builds a service provider, realizes the interface context, creates a Flask app with CORS.
3. Loads `ApiRouter` objects via `get_routers()`, maps each to a Flask `Blueprint` via `build_blueprint()`, and registers them.
4. Optionally registers the Swagger UI blueprint via `interface_context.create_swagger_blueprint()`.
5. `FlaskApiContext` (via `OpenApiContext`) handles request parsing, feature execution, error handling with status codes, and response formatting.
6. On request, `view_func` calls `context.run()` → parses request → executes feature → returns `(response, status_code)`.

### YAML Configuration

Uses the `openapi:` root key (not `flask:`):

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
  errors:
    DIVISION_BY_ZERO: 400
```

## Structured Code Style

All code follows tiferet v2 artifact comment conventions (`# ***`, `# **`, `# *`). See the [tiferet AGENTS.md](https://github.com/greatstrength/tiferet) for the full style guide.

## Testing

- **Framework:** `pytest`
- **Test location:** Co-located in `contexts/tests/` and `blueprints/tests/`.
- **Run tests:** `pytest tiferet_flask/ -v`
- **Patterns:**
  - Context tests use `mock.Mock(spec=DomainEvent)` for event dependencies and `ApiRoute`/`ApiRouter` from `tiferet_openapi`.
  - Swagger tests verify `generate_spec()` output structure and `create_swagger_blueprint()` returns a Flask Blueprint.

## Key Files

- `tiferet_flask/__init__.py` — Version and public exports
- `tiferet_flask/blueprints/flask.py` — Blueprint functions (build_flask_app, build_blueprint, get_routers, run)
- `tiferet_flask/contexts/flask.py` — FlaskApiContext (OpenApiContext subclass with Swagger)
- `tiferet_flask/contexts/request.py` — FlaskRequestContext (alias for OpenApiRequestContext)

## Migration from v0.4.x

- **Builders → Blueprints:** The `FlaskAppBuilder` class has been replaced by stateless blueprint functions in `blueprints/flask.py`. `FlaskAppBuilder()` → `build_flask_app()` / `FlaskApp()`. No more class instantiation.
- **Imports:** `from tiferet_flask import FlaskAppBuilder` → `from tiferet_flask import FlaskApp` (or `build_flask_app`).
- **Usage:** `builder = FlaskAppBuilder(); builder.run(...)` → `flask_app = FlaskApp(interface_id, view_func, swagger=True)`.
- **Dependencies:** The direct `tiferet>=2.0.0b1` dependency has been removed. Tiferet is now provided transitively through `tiferet-openapi>=0.1.3`.
- **Package layout:** `builders/` → `blueprints/`.

## Migration from v0.3.x

- **Deleted packages:** `domain/`, `interfaces/`, `events/`, `mappers/`, `repos/` — all replaced by `tiferet-openapi>=0.1.1`.
- **Contexts:** `FlaskApiContext` now extends `OpenApiContext` (not `AppInterfaceContext`). Constructor requires `get_routers_evt` in addition to `get_route_evt` and `get_status_code_evt`. `FlaskRequestContext` is now an alias for `OpenApiRequestContext`.
- **Configuration:** `flask:` root key → `openapi:` root key. `blueprints` → `routers`. `url_prefix` → `prefix`. `rule` → `path`. `flask_config_file` → `openapi_yaml_file`.
- **Imports:** Domain types (`FlaskRoute`, `FlaskBlueprint`, etc.) no longer exported from `tiferet_flask`. Import `ApiRoute`, `ApiRouter`, etc. from `tiferet_openapi`.
- **Dependency:** Added `tiferet-openapi>=0.1.1`.
