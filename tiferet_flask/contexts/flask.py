'''Flask API context.'''

# *** imports

# ** core
from contextlib import ExitStack
from importlib import resources
from typing import List

# ** infra
from flask import Blueprint, Response, jsonify, url_for
from tiferet_openapi import ApiRouter, OpenApiSessionContext

# *** constants

# ** constant: swagger_static_folder
# Resolve the vendored swagger-ui-dist tree to a real filesystem path in a
# zip-safe way; the ExitStack is intentionally never closed so the path
# stays valid for the lifetime of the process.
_SWAGGER_STATIC_RESOURCES = ExitStack()
SWAGGER_STATIC_FOLDER = str(
    _SWAGGER_STATIC_RESOURCES.enter_context(
        resources.as_file(resources.files('tiferet_flask') / 'static' / 'swagger-ui')
    )
)

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

        # Call the injected routers handler directly.
        return self._get_routers()

    # * method: create_swagger_blueprint
    def create_swagger_blueprint(self, title: str = 'API', version: str = '1.0.0', description: str = '') -> Blueprint:
        '''
        Create a Flask Blueprint serving Swagger UI and the OpenAPI spec.

        The first call snapshots the spec via get_docs_spec and caches the
        built Blueprint on the instance; later calls are a no-op that return
        the cached Blueprint without regenerating the spec.

        :param title: The API title.
        :type title: str
        :param version: The API version.
        :type version: str
        :param description: The API description.
        :type description: str
        :return: A Flask Blueprint serving /docs and /docs/openapi.json.
        :rtype: Blueprint
        '''

        # Return the cached blueprint on any call after the first.
        cached_blueprint = getattr(self, '_swagger_blueprint', None)
        if cached_blueprint is not None:
            return cached_blueprint

        # Snapshot the OpenAPI spec via the adapter-facing Publish accessor.
        spec = self.get_docs_spec(title=title, version=version, description=description)

        # Create the swagger blueprint, wired to the vendored static assets.
        swagger_bp = Blueprint(
            'swagger',
            __name__,
            url_prefix='/docs',
            static_folder=SWAGGER_STATIC_FOLDER,
            static_url_path='/assets',
        )

        # Register the JSON spec endpoint.
        @swagger_bp.route('/openapi.json')
        def openapi_json():
            return jsonify(spec)

        # Register the Swagger UI endpoint, served from vendored local assets.
        @swagger_bp.route('/')
        def swagger_ui():
            css_url = url_for('swagger.static', filename='swagger-ui.css')
            bundle_url = url_for('swagger.static', filename='swagger-ui-bundle.js')
            html = f'''<!DOCTYPE html>
<html><head><title>{title} - Docs</title>
<link rel="stylesheet" href="{css_url}">
</head><body>
<div id="swagger-ui"></div>
<script src="{bundle_url}"></script>
<script>SwaggerUIBundle({{url: "/docs/openapi.json", dom_id: "#swagger-ui"}})</script>
</body></html>'''
            return Response(html, content_type='text/html')

        # Cache the built blueprint on the instance and return it.
        self._swagger_blueprint = swagger_bp
        return swagger_bp
