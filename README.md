# Tiferet Flask - A Flask Extension for the Tiferet Framework

## Introduction

Tiferet Flask elevates the Tiferet Python framework by empowering developers to craft sophisticated Flask-based APIs rooted in Domain-Driven Design (DDD) principles. Drawing from the Kabbalistic ideal of beauty in harmony, Tiferet Flask seamlessly blends Tiferet’s command-driven architecture with Flask’s intuitive routing and request handling. The result is a powerful, modular platform for building scalable web services that distill complex business logic into elegant, extensible API designs.

This tutorial walks you through creating a streamlined calculator API, leveraging Tiferet’s robust commands and configurations while introducing Flask-specific interfaces and endpoints. For a deeper understanding of Tiferet’s foundational concepts, consult the [Tiferet documentation](https://github.com/greatstrength/tiferet).

## Getting Started with Tiferet Flask

Embark on your Tiferet Flask journey by preparing your development environment. This guide assumes familiarity with Tiferet’s core setup.

### Installing Python

Tiferet Flask requires Python 3.10 or later. Follow the detailed [Python installation instructions](https://github.com/greatstrength/tiferet?tab=readme-ov-file#installing-python) in the Tiferet README for your platform (Windows, macOS, or Linux). Verify your installation with:

```bash
python3.10 --version
```

### Setting Up a Virtual Environment

Create a dedicated virtual environment named `tiferet_flask_app` to keep dependencies organized:

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

Exit the environment with `deactivate` when finished.

## Your First Calculator API

With your environment ready, install dependencies and configure the project structure to build a dynamic calculator API using Tiferet Flask.

### Installing Tiferet Flask

In your activated virtual environment, install the Tiferet Flask extension using pip:

```bash
# Windows
pip install tiferet_flask

# macOS/Linux
pip3 install tiferet_flask
```

Note: If developing locally, replace with the appropriate local installation command.

### Project Structure

Adapt Tiferet’s project structure to incorporate Flask, adding a dedicated API script:

```plaintext
project_root/
├── basic_calc.py
├── calc_cli.py
├── calc_flask_api.py
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
        ├── flask.yml
        └── logging.yml
```

The `app/commands/` and `app/configs/` directories align with Tiferet’s structure (see [Tiferet README](https://github.com/greatstrength/tiferet?tab=readme-ov-file#project-structure)). The `calc_flask_api.py` script initializes and runs the Flask API, while `flask.yml` defines blueprint and routing configurations.

## Crafting the Calculator API

Extend Tiferet’s calculator application into a powerful API by reusing its commands and configurations, enhanced with Flask-specific functionality.

### Defining Base and Arithmetic Command Classes

Leverage Tiferet’s `BasicCalcCommand` (`app/commands/settings.py`) for input validation and arithmetic commands (`AddNumber`, `SubtractNumber`, `MultiplyNumber`, `DivideNumber`, `ExponentiateNumber` in `app/commands/calc.py`) for core operations. These remain unchanged from the original calculator app; refer to the [Tiferet README](https://github.com/greatstrength/tiferet?tab=readme-ov-file#defining-base-and-arithmetic-command-classes) for details.

### Configuring the Calculator API

Reuse Tiferet’s `container.yml` ([here](https://github.com/greatstrength/tiferet?tab=readme-ov-file#configuring-the-container-in-configscontaineryml)), `error.yml` ([here](https://github.com/greatstrength/tiferet?tab=readme-ov-file#configuring-the-errors-in-configserroryml)), and `feature.yml` ([here](https://github.com/greatstrength/tiferet?tab=readme-ov-file#configuring-the-features-in-configsfeatureyml)) for command mappings, error handling, and feature workflows. Introduce a Flask-specific interface in `app.yml` and routing configurations in `flask.yml`.

#### Configuring the App Interface in `configs/app.yml`

Enhance `app/configs/app.yml` with the `calc_flask_api` interface:

```yaml
interfaces:
  calc_flask_api:
    name: Basic Calculator API
    description: Perform basic calculator operations via Flask API
    module_path: tiferet_flask.contexts.flask
    class_name: FlaskApiContext
    attrs:
      flask_api_handler:
        module_path: tiferet_flask.handlers.flask
        class_name: FlaskApiHandler
      flask_repo:
        module_path: tiferet_flask.proxies.yaml.flask
        class_name: FlaskYamlProxy
        params:
          flask_config_file: app/configs/flask.yml
```

#### Configuring Blueprints, Routes, and Error Status Codes in `configs/flask.yml`

Define Flask API blueprints, routes, and error mappings in `app/configs/flask.yml`:

```yaml
flask:
  blueprints:
    calc:
      name: calc
      url_prefix: /calc
      routes:
        add:
          rule: /add
          methods: [POST, GET]
          status_code: 200
        subtract:
          rule: /subtract
          methods: [POST, GET]
        multiply:
          rule: /multiply
          methods: [POST, GET]
        divide:
          rule: /divide
          methods: [POST, GET]
        sqrt:
          rule: /sqrt
          methods: [POST, GET]
  errors:
    DIVIDE_BY_ZERO: 400 
```

The `url_prefix` ensures all routes are prefixed with `/calc`. Each route’s endpoint (e.g., `calc.add`) aligns with the corresponding feature ID in `feature.yml`. Routes specify a `rule`, supported HTTP `methods`, and a default `status_code` of 200. The `errors` section maps error codes from `error.yml` to HTTP status codes, ensuring proper error handling.

This configuration enables `FlaskApiContext` to orchestrate Flask API operations seamlessly.

### Initializing and Demonstrating the API in calc_flask_api.py

Create `calc_flask_api.py` to initialize the API and define endpoints:

```python
# *** imports

from tiferet import App
from tiferet_flask import FlaskApiContext

# *** functions

# * functions: view_func
def view_func(**kwargs):
    '''
    Call the view function whenever a route endpoint is invoked.

    The FlaskApiContext instance is accessed via closure (``context``),
    so it does not need to be passed explicitly as a parameter.

    :param kwargs: Additional keyword arguments.
    :type kwargs: dict
    :return: The result of the view function.
    :rtype: Any
    '''

    # Get the Flask request context.
    from flask import request, jsonify

    # Format the request data from the json payload (if applicable),
    # the query parameters, and any route parameters passed via kwargs.
    data = dict(request.json) if request.is_json else {}
    data.update(dict(request.args))
    data.update(kwargs)

    # Format header data from the request headers.
    headers = dict(request.headers)

    # Execute the feature from the request endpoint.
    response, status_code = context.run(
        feature_id=request.endpoint,
        headers=headers,
        data=data,
        **kwargs,
    )

    # Return the response as JSON.
    return jsonify(response), status_code

# *** exec

# Create the Flask API context.
context: FlaskApiContext = App().load_interface('calc_flask_api')

# Build the Flask app.
context.build_flask_app(view_func=view_func)

# Define the flask_app for external use (e.g., for Flask CLI or WSGI servers).
def flask_app():
    '''
    Create and return the Flask app for testing.

    :return: The Flask app.
    :rtype: Flask
    '''

    return context.flask_app

# Run the Flask app if this script is executed directly.
if __name__ == '__main__':
    context.flask_app.run(host='127.0.0.1', port=5000, debug=True)
```

This script initializes the Tiferet application, loads the `calc_flask_api` interface, and dynamically handles RESTful endpoints for arithmetic operations.

### Demonstrating the Calculator API

Launch the API:

```bash
python3 calc_flask_api.py
```

Test endpoints using curl or tools like Postman:

```bash
# Add two numbers
curl -X POST http://127.0.0.1:5000/calc/add -H "Content-Type: application/json" -d '{"a": 1, "b": 2}'
# Output: 3

# Calculate square root
curl -X POST http://127.0.0.1:5000/calc/sqrt -H "Content-Type: application/json" -d '{"a": 16}'
# Output: 4.0

# Division by zero
curl -X POST http://127.0.0.1:5000/calc/divide -H "Content-Type: application/json" -d '{"a": 5, "b": 0}'
# Output: {"error_code": "DIVIDE_BY_ZERO", "text": "Cannot divide by zero"}
```

## Conclusion

Tiferet Flask empowers developers to craft elegant, modular Flask APIs within Tiferet’s DDD framework, as showcased in this calculator tutorial. By seamlessly reusing Tiferet’s commands and configurations and introducing a Flask interface, you’ve built a scalable, intuitive API with minimal effort. Expand its capabilities by integrating authentication, advanced features like trigonometric operations, or combining with Tiferet’s CLI or TUI contexts. Dive into the [Tiferet documentation](https://github.com/greatstrength/tiferet) for advanced DDD techniques, and experiment with `app/configs/` to customize your API, transforming complex web applications—whether monolithic or networked—into clear, purposeful solutions.
