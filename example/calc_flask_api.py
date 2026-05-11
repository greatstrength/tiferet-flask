'''Calculator Flask API entry point.'''

# *** imports

# ** infra
from tiferet_flask import FlaskAppBuilder


# *** functions

# ** function: view_func
def view_func(**kwargs):
    '''
    Handle incoming requests by executing the corresponding feature.

    :param kwargs: Route parameters.
    :type kwargs: dict
    :return: JSON response with status code.
    :rtype: tuple
    '''

    # Get the Flask request context.
    from flask import request, jsonify

    # Format the request data from JSON payload, query params, and route params.
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
    )

    # Return the response as JSON.
    return jsonify(response), status_code


# *** exec

# Create the builder.
builder = FlaskAppBuilder()

# Build the Flask app with Swagger UI enabled.
flask_app = builder.run('calc_flask_api', view_func, swagger=True)

# Access the context for the view function closure.
context = builder.load_interface('calc_flask_api')

# Run the Flask app if executed directly.
if __name__ == '__main__':
    flask_app.run(host='127.0.0.1', port=5000, debug=True)
