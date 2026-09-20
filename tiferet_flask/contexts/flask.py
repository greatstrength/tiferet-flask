'''Flask API context.'''

# *** imports

# ** core
from typing import List

# ** infra
from flask import Blueprint, Response, jsonify
from tiferet_openapi import ApiRouter, OpenApiSessionContext


# *** contexts

# ** context: flask_api_context
class FlaskApiContext(OpenApiSessionContext):
    '''
    A Flask-specific API context extending the shared OpenAPI session hub.
    '''

    # * method: get_routers
    def get_routers(self) -> List[ApiRouter]:
        '''
        Retrieve the configured routers via the injected handler.

        :return: A list of ApiRouter domain objects.
        :rtype: List[ApiRouter]
        '''

        # Return the routers from the injected handler.
        return self._get_routers()

    # * method: create_swagger_blueprint
    def create_swagger_blueprint(self, title: str = 'API', version: str = '1.0.0', description: str = '') -> Blueprint:
        '''
        Create a Flask Blueprint serving Swagger UI and the OpenAPI spec.

        :param title: The API title.
        :type title: str
        :param version: The API version.
        :type version: str
        :param description: The API description.
        :type description: str
        :return: A Flask Blueprint serving /docs and /docs/openapi.json.
        :rtype: Blueprint
        '''

        # Generate the OpenAPI spec.
        spec = self.generate_spec(title=title, version=version, description=description)

        # Create the swagger blueprint.
        swagger_bp = Blueprint('swagger', __name__, url_prefix='/docs')

        # Register the JSON spec endpoint.
        @swagger_bp.route('/openapi.json')
        def openapi_json():
            return jsonify(spec)

        # Register the Swagger UI endpoint (CDN-hosted, no extra dependency).
        @swagger_bp.route('/')
        def swagger_ui():
            html = f'''<!DOCTYPE html>
<html><head><title>{title} - Docs</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist/swagger-ui.css">
</head><body>
<div id="swagger-ui"></div>
<script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist/swagger-ui-bundle.js"></script>
<script>SwaggerUIBundle({{url: "/docs/openapi.json", dom_id: "#swagger-ui"}})</script>
</body></html>'''
            return Response(html, content_type='text/html')

        # Return the swagger blueprint.
        return swagger_bp
