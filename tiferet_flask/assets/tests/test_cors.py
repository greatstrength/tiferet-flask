'''Flask CORS AppSession constant parser tests.'''

# *** imports

# ** infra
import pytest

# ** app
from tiferet import use_tester
from ..cors import (
    CORS_ALLOW_HEADERS_CONST_KEY,
    CORS_EXPOSE_HEADERS_CONST_KEY,
    CORS_MAX_AGE_CONST_KEY,
    CORS_METHODS_CONST_KEY,
    CORS_ORIGINS_CONST_KEY,
    CORS_SUPPORTS_CREDENTIALS_CONST_KEY,
    parse_cors_options,
)

# *** testers

# ** tester: test_parse_cors_options
@use_tester(type='generic', target_cls=parse_cors_options)
class TestParseCorsOptions:
    '''
    Tests for parse_cors_options.
    '''

    # * test: empty_constants
    def test_parse_cors_options_empty_constants(self, test_ctx, session):
        '''
        Test that empty constants return an empty kwargs dict.

        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        '''

        # Parse an empty constants map.
        result = session.given(constants={}).run(target=parse_cors_options)

        # Assert no flask-cors kwargs were produced.
        assert result == {}

    # * test: no_recognized_keys
    def test_parse_cors_options_no_recognized_keys(self, test_ctx, session):
        '''
        Test that unrelated keys return an empty kwargs dict.

        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        '''

        # Parse constants with no recognized CORS keys.
        result = session.given(
            constants={
                'timeout': '30',
                'DEBUG': 'true',
            }
        ).run(target=parse_cors_options)

        # Assert no flask-cors kwargs were produced.
        assert result == {}

    # * test: origins_wildcard
    def test_parse_cors_options_origins_wildcard(self, test_ctx, session):
        '''
        Test that a lone origins wildcard becomes the flask-cors wildcard string.

        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        '''

        # Parse a lone origins wildcard.
        result = session.given(
            constants={
                CORS_ORIGINS_CONST_KEY: '*',
            }
        ).run(target=parse_cors_options)

        # Assert flask-cors receives the wildcard string.
        assert result == {
            'origins': '*',
        }

    # * test: origins_list
    def test_parse_cors_options_origins_list(self, test_ctx, session):
        '''
        Test that comma-separated origins become a stripped token list.

        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        '''

        # Parse a comma-separated origins list.
        result = session.given(
            constants={
                CORS_ORIGINS_CONST_KEY: 'https://a.example, https://b.example',
            }
        ).run(target=parse_cors_options)

        # Assert flask-cors receives the stripped origin tokens.
        assert result == {
            'origins': [
                'https://a.example',
                'https://b.example',
            ],
        }

    # * test: origins_empty_omits_kwarg
    def test_parse_cors_options_origins_empty_omits_kwarg(self, test_ctx, session):
        '''
        Test that whitespace-only origins omit the kwarg and do not raise.

        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        '''

        # Parse whitespace-only origins.
        result = session.given(
            constants={
                CORS_ORIGINS_CONST_KEY: '   ',
            }
        ).run(target=parse_cors_options)

        # Assert the origins kwarg is omitted.
        assert result == {}

    # * test: methods_allow_headers_expose_headers
    def test_parse_cors_options_methods_allow_expose_headers(self, test_ctx, session):
        '''
        Test that methods, allow headers, and expose headers map to stripped lists.

        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        '''

        # Parse methods, allow headers, and expose headers together.
        result = session.given(
            constants={
                CORS_METHODS_CONST_KEY: 'GET, POST, OPTIONS',
                CORS_ALLOW_HEADERS_CONST_KEY: 'Content-Type, Authorization',
                CORS_EXPOSE_HEADERS_CONST_KEY: 'X-Total-Count',
            }
        ).run(target=parse_cors_options)

        # Assert each list option is stripped into flask-cors kwargs.
        assert result == {
            'methods': [
                'GET',
                'POST',
                'OPTIONS',
            ],
            'allow_headers': [
                'Content-Type',
                'Authorization',
            ],
            'expose_headers': [
                'X-Total-Count',
            ],
        }

    # * test: supports_credentials_true_tokens
    @pytest.mark.parametrize('raw_value', [
        'true',
        'True',
        '1',
        'yes',
        'YES',
    ])
    def test_parse_cors_options_supports_credentials_true(self, raw_value, test_ctx, session):
        '''
        Test that true boolean tokens set supports_credentials to True.

        :param raw_value: A recognized true token, including mixed case.
        :type raw_value: str
        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        '''

        # Parse a true credentials token.
        result = session.given(
            constants={
                CORS_SUPPORTS_CREDENTIALS_CONST_KEY: raw_value,
            }
        ).run(target=parse_cors_options)

        # Assert flask-cors receives True.
        assert result == {
            'supports_credentials': True,
        }

    # * test: supports_credentials_false_tokens
    @pytest.mark.parametrize('raw_value', [
        'false',
        'False',
        '0',
        'no',
        'NO',
    ])
    def test_parse_cors_options_supports_credentials_false(self, raw_value, test_ctx, session):
        '''
        Test that false boolean tokens set supports_credentials to False.

        :param raw_value: A recognized false token, including mixed case.
        :type raw_value: str
        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        '''

        # Parse a false credentials token.
        result = session.given(
            constants={
                CORS_SUPPORTS_CREDENTIALS_CONST_KEY: raw_value,
            }
        ).run(target=parse_cors_options)

        # Assert flask-cors receives False.
        assert result == {
            'supports_credentials': False,
        }

    # * test: supports_credentials_invalid_raises
    def test_parse_cors_options_supports_credentials_invalid_raises(self, test_ctx, session):
        '''
        Test that an unrecognized credentials token raises ValueError.

        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        '''

        # Parse an unrecognized credentials token.
        with pytest.raises(ValueError) as exc_info:
            session.given(
                constants={
                    CORS_SUPPORTS_CREDENTIALS_CONST_KEY: 'maybe',
                }
            ).run(target=parse_cors_options)

        # Assert the error names the original raw value.
        assert str(exc_info.value) == (
            "Invalid boolean value for constant 'cors_supports_credentials': 'maybe'"
        )

    # * test: max_age_valid
    def test_parse_cors_options_max_age_valid(self, test_ctx, session):
        '''
        Test that a valid max-age string becomes an integer kwarg.

        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        '''

        # Parse a valid max-age constant.
        result = session.given(
            constants={
                CORS_MAX_AGE_CONST_KEY: '600',
            }
        ).run(target=parse_cors_options)

        # Assert flask-cors receives the integer max age.
        assert result == {
            'max_age': 600,
        }

    # * test: max_age_invalid_raises
    @pytest.mark.parametrize('raw_value', [
        'not-a-number',
        '-1',
    ])
    def test_parse_cors_options_max_age_invalid_raises(self, raw_value, test_ctx, session):
        '''
        Test that non-integer and negative max-age values raise ValueError.

        :param raw_value: An invalid max-age constant string.
        :type raw_value: str
        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        '''

        # Parse an invalid max-age constant.
        with pytest.raises(ValueError) as exc_info:
            session.given(
                constants={
                    CORS_MAX_AGE_CONST_KEY: raw_value,
                }
            ).run(target=parse_cors_options)

        # Assert the error names the original raw value.
        assert str(exc_info.value) == (
            f'Invalid non-negative integer for constant {CORS_MAX_AGE_CONST_KEY!r}: {raw_value!r}'
        )

    # * test: unknown_keys_ignored
    def test_parse_cors_options_unknown_keys_ignored(self, test_ctx, session):
        '''
        Test that unknown cors_* names are ignored beside a valid origins key.

        :param test_ctx: The bound generic tester context.
        :type test_ctx: GenericTesterContext
        :param session: A fresh test session.
        :type session: TestSessionContext
        '''

        # Parse an unknown CORS key alongside a valid origins value.
        result = session.given(
            constants={
                'cors_unknown_option': 'true',
                CORS_ORIGINS_CONST_KEY: '*',
            }
        ).run(target=parse_cors_options)

        # Assert only the recognized origins kwarg is produced.
        assert result == {
            'origins': '*',
        }
