# AGENTS.md — Tiferet Flask (v0.3.0)

## Project Overview

**Tiferet Flask** is an extension of the Tiferet framework for building Flask-based APIs using Domain-Driven Design (DDD). It provides `FlaskAppBuilder`, `FlaskApiContext`, `FlaskRequestContext`, Pydantic v2 domain objects, domain events, and a YAML-backed repository for Flask configuration.

- **Repository:** https://github.com/greatstrength/tiferet-flask
- **Branch:** `main`
- **Python:** ≥ 3.10
- **Version:** `0.3.0`
- **Dependencies:** `tiferet >= 2.0.0b1`, `flask >= 3.1.2`, `flask_cors >= 6.0.1`

## Architecture

### Package Layout

```
tiferet_flask/
├── __init__.py          — Version and public exports (FlaskAppBuilder, FlaskApp)
├── builders/            — FlaskAppBuilder (AppBuilder) — primary app entry point
├── domain/              — FlaskRoute, FlaskBlueprint (DomainObject, Pydantic v2)
├── interfaces/          — FlaskApiService (Service)
├── mappers/             — Aggregates (_ROLES ClassVar) and TransferObjects for YAML round-trip
├── repos/               — FlaskYamlRepository (YamlLoader-backed FlaskApiService)
├── events/              — GetFlaskBlueprints, GetFlaskRoute, GetFlaskStatusCode (DomainEvent)
└── contexts/            — FlaskApiContext (AppInterfaceContext), FlaskRequestContext (RequestContext)
```

### Key Concepts

- **Domain Objects** (`domain/flask.py`): `FlaskRoute` and `FlaskBlueprint` — read-only Pydantic v2 domain models extending `DomainObject` with `Field` annotations. `FlaskRoute` includes an `endpoint` field (format: `blueprint_name.route_id`).
- **Service Interface** (`interfaces/flask.py`): `FlaskApiService` — abstract contract for Flask API configuration access (`get_blueprints`, `get_route`, `get_status_code`). Returns domain objects, not aggregates.
- **Mappers** (`mappers/flask.py`): `FlaskRouteAggregate`, `FlaskBlueprintAggregate` (mutable, direct Pydantic constructors), `FlaskRouteYamlObject`, `FlaskBlueprintYamlObject` (serialization via `_ROLES` ClassVar, `model_validate`, `@classmethod from_model`).
- **Repository** (`repos/flask.py`): `FlaskYamlRepository` — `YamlLoader`-backed implementation of `FlaskApiService`. Uses `model_validate()` for YAML object construction. Constructor param: `flask_yaml_file`.
- **Domain Events** (`events/flask.py`): `GetFlaskBlueprints`, `GetFlaskRoute`, `GetFlaskStatusCode` — receive `FlaskApiService` via constructor injection. Return domain objects.
- **Contexts** (`contexts/flask.py`): `FlaskApiContext` — receives `DomainEvent` instances (`get_route_evt`, `get_status_code_evt`), wraps `.execute` internally. `handle_error` raises `TiferetAPIError` with `status_code`. `FlaskRequestContext` serializes via `BaseModel.model_dump()`.
- **Builder** (`builders/flask.py`): `FlaskAppBuilder` — extends `tiferet.builders.AppBuilder`. Primary entry point for constructing Flask applications. Resolves `get_blueprints_evt` from service provider. Exported as `FlaskApp` alias.

### Runtime Flow

1. `FlaskAppBuilder()` (or `FlaskApp()`) loads settings and service provider.
2. `builder.run(interface_id, view_func)` loads the interface, assembles blueprints, and returns a Flask app.
3. `FlaskApiContext` is instantiated with `DomainEvent` instances for route and status code lookup.
4. On request, `view_func` calls `context.run()` which parses the request, executes the feature, and returns a response with status code.
5. `handle_error` raises `TiferetAPIError` with `status_code` attribute for error responses.

## Structured Code Style

All code follows tiferet v2 artifact comment conventions (`# ***`, `# **`, `# *`). See the [tiferet AGENTS.md](https://github.com/greatstrength/tiferet) for the full style guide.

## Testing

- **Framework:** `pytest`
- **Test location:** Co-located in `<package>/tests/` directories.
- **Run tests:** `pytest tiferet_flask/ -v`
- **Patterns:**
  - Domain/mapper tests use direct Pydantic constructors.
  - Event tests use `DomainEvent.handle()` with mocked `FlaskApiService`.
  - Repo tests are integration tests using `tmp_path` with real YAML files.
  - Context tests use `mock.Mock(spec=DomainEvent)` for event dependencies.

## Key Files

- `tiferet_flask/__init__.py` — Version and public exports
- `tiferet_flask/builders/flask.py` — FlaskAppBuilder
- `tiferet_flask/domain/flask.py` — FlaskRoute, FlaskBlueprint domain objects
- `tiferet_flask/interfaces/flask.py` — FlaskApiService interface
- `tiferet_flask/mappers/flask.py` — Aggregates and TransferObjects
- `tiferet_flask/repos/flask.py` — FlaskYamlRepository
- `tiferet_flask/events/flask.py` — Domain events
- `tiferet_flask/contexts/flask.py` — FlaskApiContext
- `tiferet_flask/contexts/request.py` — FlaskRequestContext

## Migration from v0.2.x

- **Domain:** Schematics type descriptors → Pydantic v2 `Field` annotations. Added `endpoint` field to `FlaskRoute`.
- **Mappers:** `Aggregate.new()` → direct Pydantic constructor. `class Options` → `_ROLES` ClassVar. `from_data()` → `model_validate()`. `from_model` → `@classmethod`.
- **Interfaces:** Return types changed from aggregates to domain objects. Removed `exists`, `save`, `delete`.
- **Events:** Return types changed from aggregates to domain objects. Imports from `..domain` instead of `..mappers`.
- **Repository:** `Yaml` shorthand → `YamlLoader` composition. `flask_config_file` → `flask_yaml_file`. Removed `exists`, `save`, `delete`.
- **Contexts:** `FlaskApiContext` accepts `DomainEvent` instances (not callables). Removed `build_blueprint`, `build_flask_app`, `get_blueprints_handler`, `flask_app`. `handle_error` raises `TiferetAPIError` (not tuple). `FlaskRequestContext` uses `BaseModel.model_dump()`.
- **Builders:** New `FlaskAppBuilder` extending `AppBuilder`. Primary entry point for app construction.
- **Dependency:** `tiferet>=2.0.0a8` → `tiferet>=2.0.0b1`.
