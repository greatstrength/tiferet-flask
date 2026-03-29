# AGENTS.md — Tiferet Flask (v0.2.0)

## Project Overview

**Tiferet Flask** is an extension of the Tiferet framework for building Flask-based APIs using Domain-Driven Design (DDD). It provides `FlaskApiContext`, `FlaskRequestContext`, domain objects, domain events, and a YAML-backed repository for Flask configuration.

- **Repository:** https://github.com/greatstrength/tiferet-flask
- **Branch:** `main`
- **Python:** ≥ 3.10
- **Version:** `0.2.0`
- **Dependencies:** `tiferet >= 2.0.0a8`, `flask >= 3.1.2`, `flask_cors >= 6.0.1`

## Architecture

### Package Layout

```
tiferet_flask/
├── __init__.py          — Version and public exports
├── domain/              — FlaskRoute, FlaskBlueprint (DomainObject)
├── interfaces/          — FlaskApiService (Service)
├── mappers/             — Aggregates and TransferObjects for YAML round-trip
├── repos/               — FlaskYamlRepository (YAML-backed FlaskApiService)
├── events/              — GetFlaskBlueprints, GetFlaskRoute, GetFlaskStatusCode (DomainEvent)
└── contexts/            — FlaskApiContext (AppInterfaceContext), FlaskRequestContext (RequestContext)
```

### Key Concepts

- **Domain Objects** (`domain/flask.py`): `FlaskRoute` and `FlaskBlueprint` — read-only domain models extending `DomainObject`.
- **Service Interface** (`interfaces/flask.py`): `FlaskApiService` — abstract contract for Flask API configuration access (exists, get_blueprints, get_route, get_status_code, save, delete).
- **Mappers** (`mappers/flask.py`): `FlaskRouteAggregate`, `FlaskBlueprintAggregate` (mutable), `FlaskRouteYamlObject`, `FlaskBlueprintYamlObject` (serialization).
- **Repository** (`repos/flask.py`): `FlaskYamlRepository` — YAML-backed implementation of `FlaskApiService` using the `Yaml` utility.
- **Domain Events** (`events/flask.py`): `GetFlaskBlueprints`, `GetFlaskRoute`, `GetFlaskStatusCode` — receive `FlaskApiService` via constructor injection.
- **Contexts** (`contexts/flask.py`): `FlaskApiContext` — receives three callable handlers (`get_blueprints_handler`, `get_route_handler`, `get_status_code_handler`) resolved by the DI container.

### Runtime Flow

1. `App()` loads settings and resolves the `calc_flask_api` interface.
2. `FlaskApiContext` is instantiated with callable handlers backed by domain events.
3. `build_flask_app()` calls `get_blueprints_handler()` to load blueprints and register Flask routes.
4. On request, `view_func` calls `context.run()` which parses the request, executes the feature, and returns a response with status code.
5. `handle_error` catches `TiferetAPIError` from the parent and returns a dict + status code tuple.

## Structured Code Style

All code follows tiferet v2 artifact comment conventions (`# ***`, `# **`, `# *`). See the [tiferet AGENTS.md](https://github.com/greatstrength/tiferet) for the full style guide.

## Testing

- **Framework:** `pytest`
- **Test location:** Co-located in `<package>/tests/` directories.
- **Run tests:** `pytest tiferet_flask/ -v`
- **Patterns:**
  - Domain/mapper tests use `DomainObject.new()` and `Aggregate.new()`.
  - Event tests use `DomainEvent.handle()` with mocked `FlaskApiService`.
  - Repo tests are integration tests using `tmp_path` with real YAML files.
  - Context tests use `mock.Mock()` callables for handler dependencies.

## Key Files

- `tiferet_flask/__init__.py` — Version and public exports
- `tiferet_flask/domain/flask.py` — FlaskRoute, FlaskBlueprint domain objects
- `tiferet_flask/interfaces/flask.py` — FlaskApiService interface
- `tiferet_flask/mappers/flask.py` — Aggregates and TransferObjects
- `tiferet_flask/repos/flask.py` — FlaskYamlRepository
- `tiferet_flask/events/flask.py` — Domain events
- `tiferet_flask/contexts/flask.py` — FlaskApiContext
- `tiferet_flask/contexts/request.py` — FlaskRequestContext
