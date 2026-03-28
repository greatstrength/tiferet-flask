"""Test application for the Flask API with Tiferet"""

# *** imports

# ** infra
from tiferet import App
from tiferet_flask import FlaskApiContext

# *** functions

# * functions: view_func
def view_func(**kwargs):
    '''
    Call the view function.

    :param context: The Flask API context.
    :type context: FlaskApiContext
    :param kwargs: Additional keyword arguments.
    :type kwargs: dict
    :return: The result of the view function.
    :rtype: Any
    '''

    # Get the Flask request context.
    from flask import request, jsonify

    # Format the request data from the json payload (if applicable) and the query parameters
    data = dict(request.json) if request.is_json else {}
    data.update(dict(request.args))
    data.update(dict(request.view_args))

    # Format header data from the request headers and authorization by type (if applicable)
    headers = dict(request.headers)
    headers.update({
        'Tiferet-Auth-Type': request.authorization.type,
        'Tiferet-Auth-Token': request.authorization.token,
        'Tiferet-Auth-Params': dict(request.authorization.parameters)
    }) if request.authorization else {}

    # Execute the feature from the request endpoint
    response, status_code = context.run(
        feature_id=request.endpoint, 
        headers=headers, 
        data=data,
        **kwargs
    )

    # Return the response as JSON.
    return jsonify(response), status_code

# *** exec

# Create the Flask API context.
context: FlaskApiContext = App().load_interface('test_flask')

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
