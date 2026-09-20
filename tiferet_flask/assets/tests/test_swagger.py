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
    Verify SWAGGER_STATIC_FOLDER resolves to a real directory containing the
    vendored swagger-ui-dist CSS and JS bundle files (RFP-003 item 5).
    '''

    # Verify the resolved directory exists on disk.
    assert os.path.isdir(SWAGGER_STATIC_FOLDER)

    # Verify the vendored asset files are present in that directory.
    assert os.path.isfile(os.path.join(SWAGGER_STATIC_FOLDER, SWAGGER_UI_CSS_FILENAME))
    assert os.path.isfile(os.path.join(SWAGGER_STATIC_FOLDER, SWAGGER_UI_BUNDLE_JS_FILENAME))

# *** testers

# ** tester: test_build_swagger_ui_html
@use_tester(
    type='generic',
    target_cls=build_swagger_ui_html,
)
class TestBuildSwaggerUiHtml:
    '''
    Generic tester for build_swagger_ui_html.
    '''

    # * test: interpolates_title_and_asset_urls
    def test_build_swagger_ui_html_interpolates_title_and_asset_urls(self, session) -> None:
        '''
        Verify the rendered HTML interpolates the title and the given local
        asset URLs.
        '''

        # Exercise build_swagger_ui_html with local asset URLs.
        result = session.given(
            title='Test API',
            css_url='/docs/assets/swagger-ui.css',
            bundle_url='/docs/assets/swagger-ui-bundle.js',
            openapi_json_url='/docs/openapi.json',
        ).run(target=build_swagger_ui_html)

        # Assert the title and asset URLs are present.
        assert 'Test API - Docs' in result
        assert '/docs/assets/swagger-ui.css' in result
        assert '/docs/assets/swagger-ui-bundle.js' in result
        assert '/docs/openapi.json' in result

    # * test: has_no_cdn_hosts
    def test_build_swagger_ui_html_has_no_cdn_hosts(self, session) -> None:
        '''
        Verify the rendered HTML never references a CDN host, regardless of
        the given asset URLs (RFP-003 AC).
        '''

        # Exercise build_swagger_ui_html with local asset URLs.
        result = session.given(
            title='Test API',
            css_url='/docs/assets/swagger-ui.css',
            bundle_url='/docs/assets/swagger-ui-bundle.js',
            openapi_json_url='/docs/openapi.json',
        ).run(target=build_swagger_ui_html)

        # Assert no CDN host is referenced.
        assert 'jsdelivr' not in result
        assert 'cdn.jsdelivr.net' not in result
