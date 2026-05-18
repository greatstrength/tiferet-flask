# Calculator Flask API Example

A self-contained calculator API demonstrating the Tiferet Flask v0.5.0 architecture with Swagger UI support.

## Prerequisites

- Python 3.10+
- Virtual environment (recommended)

## Setup

```bash
# Create and activate a virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install tiferet-flask
pip install tiferet-flask
```

## Run

```bash
cd example
python calc_flask_api.py
```

The server starts at `http://127.0.0.1:5000`.

## Endpoints

All endpoints accept both `POST` (JSON body) and `GET` (query parameters).

### Addition — `/calc/add`

```bash
curl -X POST http://127.0.0.1:5000/calc/add \
  -H "Content-Type: application/json" -d '{"a": 1, "b": 2}'
# Output: 3
```

### Subtraction — `/calc/subtract`

```bash
curl -X POST http://127.0.0.1:5000/calc/subtract \
  -H "Content-Type: application/json" -d '{"a": 10, "b": 3}'
# Output: 7
```

### Multiplication — `/calc/multiply`

```bash
curl -X POST http://127.0.0.1:5000/calc/multiply \
  -H "Content-Type: application/json" -d '{"a": 4, "b": 5}'
# Output: 20
```

### Division — `/calc/divide`

```bash
curl -X POST http://127.0.0.1:5000/calc/divide \
  -H "Content-Type: application/json" -d '{"a": 10, "b": 2}'
# Output: 5.0
```

### Square Root — `/calc/sqrt`

```bash
curl -X POST http://127.0.0.1:5000/calc/sqrt \
  -H "Content-Type: application/json" -d '{"a": 16}'
# Output: 4.0
```

## Error Handling

### Division by Zero

```bash
curl -X POST http://127.0.0.1:5000/calc/divide \
  -H "Content-Type: application/json" -d '{"a": 5, "b": 0}'
# HTTP 400: {"error_code": "DIVISION_BY_ZERO", "name": "Division By Zero", "message": "Cannot divide by zero"}
```

### Invalid Input

```bash
curl -X POST http://127.0.0.1:5000/calc/add \
  -H "Content-Type: application/json" -d '{"a": "abc", "b": 2}'
# HTTP 422: {"error_code": "INVALID_INPUT", "name": "Invalid Numeric Input", "message": "Value abc must be a number"}
```

## Swagger UI

Browse the interactive API documentation at:

- **Swagger UI:** http://127.0.0.1:5000/docs
- **OpenAPI spec:** http://127.0.0.1:5000/docs/openapi.json

## Project Structure

```
example/
├── calc_flask_api.py           # Flask API entry point
├── README.md                   # This file
└── app/
    ├── events/
    │   ├── __init__.py
    │   └── calc.py             # Arithmetic domain events
    ├── utils/
    │   ├── __init__.py
    │   └── calc.py             # Number validation utility
    └── configs/
        ├── app.yml             # Interface definitions
        ├── openapi.yml         # Routers, routes, and error status codes
        ├── container.yml       # DI mappings for events
        ├── error.yml           # Structured error messages
        └── feature.yml         # Feature workflows
```
