'''Tiferet Flask swagger asset tests.'''

# *** imports

# ** core
import os

# ** infra
from tiferet import use_tester

# ** app
from ..swagger import (
    SWAGGER_STATIC_FOLDER,
    SWAGGER_UI_BUNDLE_JS_FILENAME,
    SWAGGER_UI_CSS_FILENAME,
    build_swagger_ui_html,
)

# *** tests

# ** test: swagger_static_folder_contains_vendored_assets
def test_swagger_static_folder_contains_vendored_assets():
    '''
    Assert the resolved static folder contains the vendored CSS and JS files.
    '''

    # Assert the resolved folder and vendored filenames exist on disk.
    assert os.path.isdir(SWAGGER_STATIC_FOLDER)
    assert os.path.isfile(os.path.join(SWAGGER_STATIC_FOLDER, SWAGGER_UI_CSS_FILENAME))
    assert os.path.isfile(os.path.join(SWAGGER_STATIC_FOLDER, SWAGGER_UI_BUNDLE_JS_FILENAME))

# *** testers

# ** tester: test_build_swagger_ui_html
@use_tester(type='generic', target_cls=build_swagger_ui_html)
class TestBuildSwaggerUiHtml:
    '''
    Tests for build_swagger_ui_html.
    '''

    # * test: interpolates_title_and_asset_urls
    def test_build_swagger_ui_html_interpolates_title_and_asset_urls(self, session):
        '''
        Test that the HTML interpolates the title and local asset URLs.

        :param session: A fresh test session.
        :type session: TestSessionContext
        '''

        # Build the Swagger UI document from local asset URLs.
        result = session.given(
            title='Test API',
            css_url='/docs/assets/swagger-ui.css',
            bundle_url='/docs/assets/swagger-ui-bundle.js',
            openapi_json_url='/docs/openapi.json',
        ).run(target=build_swagger_ui_html)

        # Assert the title and local URLs are interpolated.
        assert 'Test API - Docs' in result
        assert '/docs/assets/swagger-ui.css' in result
        assert '/docs/assets/swagger-ui-bundle.js' in result
        assert '/docs/openapi.json' in result

    # * test: has_no_cdn_hosts
    def test_build_swagger_ui_html_has_no_cdn_hosts(self, session):
        '''
        Test that the HTML contains no CDN hosts.

        :param session: A fresh test session.
        :type session: TestSessionContext
        '''

        # Build the Swagger UI document from local asset URLs.
        result = session.given(
            title='Test API',
            css_url='/docs/assets/swagger-ui.css',
            bundle_url='/docs/assets/swagger-ui-bundle.js',
            openapi_json_url='/docs/openapi.json',
        ).run(target=build_swagger_ui_html)

        # Assert no jsDelivr or CDN hosts are present.
        assert 'jsdelivr' not in result
        assert 'cdn.jsdelivr.net' not in result
