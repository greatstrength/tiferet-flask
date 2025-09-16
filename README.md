# Tiferet Flask - A Flask Extension for the Tiferet Framework

## Introduction

Tiferet Flask is an extension of the Tiferet Python framework, enabling developers to build robust Flask-based APIs using Domain-Driven Design (DDD) principles. Inspired by the concept of beauty in harmony reflected in form, Tiferet Flask integrates Tiferet's command and configuration-driven approach with Flask's routing and request handling to create scalable, modular web services. It transforms complex business logic into clear, extensible API models that resonate with precision and elegance.

This tutorial guides you through building a simple calculator API, reusing Tiferet's commands and configurations while adding Flask-specific interfaces and endpoints. For foundational Tiferet concepts, refer to the [Tiferet documentation](https://github.com/greatstrength/tiferet).

## Getting Started with Tiferet Flask

Set up your environment to start building with Tiferet Flask, assuming familiarity with Tiferet's core setup.

### Installing Python

Tiferet Flask requires Python 3.10 or later. Follow the Tiferet README's Python installation instructions for your platform (Windows, macOS, or Linux). Verify with:

```bash
python3.10 --version
```

### Setting Up a Virtual Environment

Create and activate a virtual environment named `tiferet_flask_app`:

```bash
# Create the Environment
# Windows
python -m venv tiferet_flask_app

# macOS/Linux
python3.10 -m venv tiferet_flask_app

# Activate the Environment
# Windows (Command Prompt)
tiferet_flask_app\Scripts\activate

# Windows (PowerShell)
.\tiferet_flask_app\Scripts\Activate.ps1

# macOS/Linux
source tiferet_flask_app/bin/activate
```

Deactivate with `deactivate` when done.

## Your First Calculator API

Install dependencies and set up the project structure to build a calculator API with Tiferet Flask.

### Installing Tiferet Flask

Install Tiferet, Flask, and the Tiferet Flask extension (replace with local installation if developing):

```bash
pip install tiferet tiferet-flask flask
```

### Project Structure

Adapt Tiferet's structure for Flask, adding an API script:

```plaintext
project_root/
├── basic_calc_api.py
├── app/
    ├── commands/
    │   ├── __init__.py
    │   ├── calc.py
    │   └── settings.py
    └── configs/
        ├── __init__.py
        ├── app.yml
        ├── container.yml
        ├── error.yml
        ├── feature.yml
        └── logging.yml
```

The `app/commands/` and `app/configs/` directories mirror Tiferet's structure (see Tiferet README). The `basic_calc_api.py` script initializes and runs the Flask API.

## Crafting the Calculator API

Reuse Tiferet's commands and configurations, adding a Flask-specific interface for API functionality.

### Defining Base and Arithmetic Command Classes

Use Tiferet's `BasicCalcCommand` (`app/commands/settings.py`) for numeric validation and arithmetic commands (`AddNumber`, `SubtractNumber`, `MultiplyNumber`, `DivideNumber`, `ExponentiateNumber` in `app/commands/calc.py`) for operations. These files are unchanged from the Tiferet README; refer there for full content.

### Configuring the Calculator API

Reuse Tiferet's `container.yml`, `error.yml`, and `feature.yml` for command mappings, error handling, and feature workflows. Add a Flask interface in `app.yml`.

#### Configuring the App Interface in `configs/app.yml`

Update `app/configs/app.yml` to include the `basic_calc_api` interface:

```yaml
interfaces:
  basic_calc_api:
    name: Basic Calculator API
    description: Perform basic calculator operations via Flask API
    module_path: tiferet_flask.contexts.flask
    class_name: FlaskContext
    attrs:
      flask_app:
        module_path: flask
        class_name: Flask
        params:
          import_name: __name__
```

This configures `FlaskContext` (assumed in Tiferet Flask) for Flask integration. Reference Tiferet's `container.yml`, `error.yml`, and `feature.yml` without modifications.

### Initializing and Demonstrating the API in basic_calc_api.py

Create `basic_calc_api.py` to define API endpoints:

```python
from tiferet import App
from tiferet_flask import FlaskContext
from flask import request, jsonify

app_manager = App()
api = app_manager.load_interface('basic_calc_api')
flask_app = api.flask_app

@flask_app.route('/calc/add', methods=['POST'])
def add():
    data = request.json
    try:
        result = app_manager.run('basic_calc_api', 'calc.add', data={'a': data['a'], 'b': data['b']})
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@flask_app.route('/calc/subtract', methods=['POST'])
def subtract():
    data = request.json
    try:
        result = app_manager.run('basic_calc_api', 'calc.subtract', data={'a': data['a'], 'b': data['b']})
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@flask_app.route('/calc/multiply', methods=['POST'])
def multiply():
    data = request.json
    try:
        result = app_manager.run('basic_calc_api', 'calc.multiply', data={'a': data['a'], 'b': data['b']})
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@flask_app.route('/calc/divide', methods=['POST'])
def divide():
    data = request.json
    try:
        result = app_manager.run('basic_calc_api', 'calc.divide', data={'a': data['a'], 'b': data['b']})
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@flask_app.route('/calc/exp', methods=['POST'])
def exp():
    data = request.json
    try:
        result = app_manager.run('basic_calc_api', 'calc.exp', data={'a': data['a'], 'b': data['b']})
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@flask_app.route('/calc/sqrt', methods=['POST'])
def sqrt():
    data = request.json
    try:
        result = app_manager.run('basic_calc_api', 'calc.sqrt', data={'a': data['a']})
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    flask_app.run(debug=True)
```

This script initializes the Tiferet app, loads the `basic_calc_api` interface, and defines RESTful endpoints for arithmetic operations.

### Demonstrating the Calculator API

Run the API:

```bash
python basic_calc_api.py
```

Test endpoints using curl or a tool like Postman:

```bash
# Add two numbers
curl -X POST http://127.0.0.1:5000/calc/add -H "Content-Type: application/json" -d '{"a": 1, "b": 2}'
# Output: {"result": 3}

# Calculate square root
curl -X POST http://127.0.0.1:5000/calc/sqrt -H "Content-Type: application/json" -d '{"a": 16}'
# Output: {"result": 4.0}

# Division by zero
curl -X POST http://127.0.0.1:5000/calc/divide -H "Content-Type: application/json" -d '{"a": 5, "b": 0}'
# Output: {"error": "Cannot divide by zero"}
```

## Conclusion

Tiferet Flask extends Tiferet's DDD framework to create elegant, modular Flask APIs, as demonstrated in this calculator tutorial. By reusing Tiferet's commands and configurations and adding a Flask interface, you've built a scalable API with minimal setup. Extend further by adding authentication, advanced features (e.g., trigonometric operations), or integrating with other Tiferet contexts like CLI or TUI. Explore the Tiferet documentation for deeper DDD techniques, and experiment with configurations in `app/configs/` to tailor your API.