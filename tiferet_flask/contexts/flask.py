'''Flask API context.'''

# *** imports

# ** core
from typing import List

# ** infra
from flask import Blueprint, Response, jsonify, url_for
from tiferet_openapi import ApiRouter, OpenApiSessionContext

# ** app
from ..assets.swagger import (
    DEFAULT_API_DESCRIPTION,
    DEFAULT_API_TITLE,
    DEFAULT_API_VERSION,
    SWAGGER_BLUEPRINT_NAME,
    SWAGGER_OPENAPI_JSON_PATH,
    SWAGGER_STATIC_FOLDER,
    SWAGGER_STATIC_URL_PATH,
    SWAGGER_UI_BUNDLE_JS_FILENAME,
    SWAGGER_UI_CSS_FILENAME,
    SWAGGER_URL_PREFIX,
    build_swagger_ui_html,
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

        # Return the routers from the injected handler.
        return self._get_routers()

    # * method: create_swagger_blueprint
    def create_swagger_blueprint(self,
            title: str = DEFAULT_API_TITLE,
            version: str = DEFAULT_API_VERSION,
            description: str = DEFAULT_API_DESCRIPTION) -> Blueprint:
        '''
        Create a Flask Blueprint serving Swagger UI and the OpenAPI spec.

        The first call snapshots the spec via get_docs_spec and caches the
        Blueprint. Later calls are a no-op that return the cached Blueprint
        without regenerating the spec.

        :param title: The API title.
        :type title: str
        :param version: The API version.
        :type version: str
        :param description: The API description.
        :type description: str
        :return: A Flask Blueprint serving /docs and /docs/openapi.json.
        :rtype: Blueprint
        '''

        # Return the cached blueprint when already built.
        swagger_bp = getattr(self, '_swagger_blueprint', None)
        if swagger_bp is not None:
            return swagger_bp

        # Snapshot the OpenAPI spec on the first call.
        spec = self.get_docs_spec(
            title=title,
            version=version,
            description=description,
        )

        # Create the swagger blueprint wired to vendored UI assets.
        swagger_bp = Blueprint(
            SWAGGER_BLUEPRINT_NAME,
            __name__,
            url_prefix=SWAGGER_URL_PREFIX,
            static_folder=SWAGGER_STATIC_FOLDER,
            static_url_path=SWAGGER_STATIC_URL_PATH,
        )

        # Register the JSON spec endpoint.
        @swagger_bp.route('/openapi.json')
        def openapi_json():
            return jsonify(spec)

        # Register the Swagger UI endpoint from vendored assets.
        @swagger_bp.route('/')
        def swagger_ui():
            html = build_swagger_ui_html(
                title,
                css_url=url_for(
                    f'{SWAGGER_BLUEPRINT_NAME}.static',
                    filename=SWAGGER_UI_CSS_FILENAME,
                ),
                bundle_url=url_for(
                    f'{SWAGGER_BLUEPRINT_NAME}.static',
                    filename=SWAGGER_UI_BUNDLE_JS_FILENAME,
                ),
                openapi_json_url=SWAGGER_OPENAPI_JSON_PATH,
            )
            return Response(html, content_type='text/html')

        # Cache the blueprint on the instance.
        self._swagger_blueprint = swagger_bp

        # Return the swagger blueprint.
        return swagger_bp
