'''Tiferet Flask Swagger Assets'''

# *** imports

# ** core
from contextlib import ExitStack
from importlib import resources

# *** constants

# ** constant: swagger_blueprint_name
SWAGGER_BLUEPRINT_NAME = 'swagger'

# ** constant: swagger_url_prefix
SWAGGER_URL_PREFIX = '/docs'

# ** constant: swagger_static_url_path
SWAGGER_STATIC_URL_PATH = '/assets'

# ** constant: swagger_ui_css_filename
SWAGGER_UI_CSS_FILENAME = 'swagger-ui.css'

# ** constant: swagger_ui_bundle_js_filename
SWAGGER_UI_BUNDLE_JS_FILENAME = 'swagger-ui-bundle.js'

# ** constant: swagger_openapi_json_path
SWAGGER_OPENAPI_JSON_PATH = '/docs/openapi.json'

# ** constant: default_api_title
DEFAULT_API_TITLE = 'API'

# ** constant: default_api_version
DEFAULT_API_VERSION = '1.0.0'

# ** constant: default_api_description
DEFAULT_API_DESCRIPTION = ''

# ** constant: swagger_static_folder
_SWAGGER_STATIC_RESOURCES = ExitStack()
SWAGGER_STATIC_FOLDER = str(_SWAGGER_STATIC_RESOURCES.enter_context(
    resources.as_file(resources.files('tiferet_flask') / 'static' / 'swagger-ui')
))

# *** functions

# ** function: build_swagger_ui_html
def build_swagger_ui_html(title: str,
        css_url: str,
        bundle_url: str,
        openapi_json_url: str) -> str:
    '''
    Build the Swagger UI HTML document from local asset URLs.

    :param title: API title shown in the page <title> tag.
    :type title: str
    :param css_url: URL serving the vendored swagger-ui.css.
    :type css_url: str
    :param bundle_url: URL serving the vendored swagger-ui-bundle.js.
    :type bundle_url: str
    :param openapi_json_url: URL serving the generated OpenAPI spec.
    :type openapi_json_url: str
    :return: Rendered Swagger UI HTML document.
    :rtype: str
    '''

    # Return the interpolated Swagger UI document.
    return f'''<!DOCTYPE html>
<html><head><title>{title} - Docs</title>
<link rel="stylesheet" href="{css_url}">
</head><body>
<div id="swagger-ui"></div>
<script src="{bundle_url}"></script>
<script>SwaggerUIBundle({{url: "{openapi_json_url}", dom_id: "#swagger-ui"}})</script>
</body></html>'''
