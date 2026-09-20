# *** imports

# ** infra
import pytest
from tiferet import use_tester

# ** app
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
@use_tester(
    type='generic',
    target_cls=parse_cors_options,
)
class TestParseCorsOptions:
    '''
    Generic tester for parse_cors_options, covering the closed cors_* key
    set and its encodings (RFP-004 AC).
    '''

    # * test: empty_constants
    def test_parse_cors_options_empty_constants(self, session) -> None:
        '''
        Verify an empty constants map returns an empty dict.
        '''

        # Exercise parse_cors_options with an empty constants map.
        result = session.given(constants={}).run(target=parse_cors_options)

        # Assert no kwargs are returned.
        assert result == {}

    # * test: no_recognized_keys
    def test_parse_cors_options_no_recognized_keys(self, session) -> None:
        '''
        Verify constants with no recognized cors_* keys return an empty dict.
        '''

        # Exercise parse_cors_options with unrelated constants.
        result = session.given(constants={'timeout': '30', 'DEBUG': '1'}).run(target=parse_cors_options)

        # Assert no kwargs are returned.
        assert result == {}

    # * test: origins_wildcard
    def test_parse_cors_options_origins_wildcard(self, session) -> None:
        '''
        Verify a lone '*' origins token is passed as the wildcard string.
        '''

        # Exercise parse_cors_options with a wildcard origins constant.
        result = session.given(constants={CORS_ORIGINS_CONST_KEY: '*'}).run(target=parse_cors_options)

        # Assert the wildcard string form.
        assert result == {'origins': '*'}

    # * test: origins_list
    def test_parse_cors_options_origins_list(self, session) -> None:
        '''
        Verify comma-separated origins are split, stripped, and returned as
        a list.
        '''

        # Exercise parse_cors_options with two comma-separated origins.
        result = session.given(
            constants={CORS_ORIGINS_CONST_KEY: 'https://a.example, https://b.example'},
        ).run(target=parse_cors_options)

        # Assert the parsed origin list.
        assert result == {'origins': ['https://a.example', 'https://b.example']}

    # * test: origins_empty_omits_kwarg
    def test_parse_cors_options_origins_empty_omits_kwarg(self, session) -> None:
        '''
        Verify an empty or whitespace-only origins value omits the kwarg
        rather than raising.
        '''

        # Exercise parse_cors_options with a whitespace-only origins value.
        result = session.given(constants={CORS_ORIGINS_CONST_KEY: '   '}).run(target=parse_cors_options)

        # Assert no kwargs are returned.
        assert result == {}

    # * test: methods_allow_headers_expose_headers
    def test_parse_cors_options_methods_allow_expose_headers(self, session) -> None:
        '''
        Verify cors_methods, cors_allow_headers, and cors_expose_headers map
        to their flask-cors kwargs using the same list encoding.
        '''

        # Exercise parse_cors_options with the remaining three list keys.
        result = session.given(constants={
            CORS_METHODS_CONST_KEY: 'GET, POST, OPTIONS',
            CORS_ALLOW_HEADERS_CONST_KEY: 'Content-Type, Authorization',
            CORS_EXPOSE_HEADERS_CONST_KEY: 'X-Total-Count',
        }).run(target=parse_cors_options)

        # Assert each key maps to its flask-cors kwarg.
        assert result == {
            'methods': ['GET', 'POST', 'OPTIONS'],
            'allow_headers': ['Content-Type', 'Authorization'],
            'expose_headers': ['X-Total-Count'],
        }

    # * test: supports_credentials_true_tokens
    @pytest.mark.parametrize('raw_value', ['true', 'True', '1', 'yes', 'YES'])
    def test_parse_cors_options_supports_credentials_true(self, session, raw_value: str) -> None:
        '''
        Verify case-insensitive true-like tokens parse to True.
        '''

        # Exercise parse_cors_options with a true-like token.
        result = session.given(constants={CORS_SUPPORTS_CREDENTIALS_CONST_KEY: raw_value}).run(target=parse_cors_options)

        # Assert the boolean kwarg is True.
        assert result == {'supports_credentials': True}

    # * test: supports_credentials_false_tokens
    @pytest.mark.parametrize('raw_value', ['false', 'False', '0', 'no', 'NO'])
    def test_parse_cors_options_supports_credentials_false(self, session, raw_value: str) -> None:
        '''
        Verify case-insensitive false-like tokens parse to False.
        '''

        # Exercise parse_cors_options with a false-like token.
        result = session.given(constants={CORS_SUPPORTS_CREDENTIALS_CONST_KEY: raw_value}).run(target=parse_cors_options)

        # Assert the boolean kwarg is False.
        assert result == {'supports_credentials': False}

    # * test: supports_credentials_invalid_raises
    def test_parse_cors_options_supports_credentials_invalid_raises(self, session) -> None:
        '''
        Verify an unrecognized boolean token raises ValueError.
        '''

        # Exercise parse_cors_options with an invalid boolean token.
        with pytest.raises(ValueError):
            session.given(constants={CORS_SUPPORTS_CREDENTIALS_CONST_KEY: 'maybe'}).run(target=parse_cors_options)

    # * test: max_age_valid
    def test_parse_cors_options_max_age_valid(self, session) -> None:
        '''
        Verify a valid non-negative integer string parses to an int.
        '''

        # Exercise parse_cors_options with a valid max_age constant.
        result = session.given(constants={CORS_MAX_AGE_CONST_KEY: '600'}).run(target=parse_cors_options)

        # Assert the parsed integer kwarg.
        assert result == {'max_age': 600}

    # * test: max_age_invalid_raises
    @pytest.mark.parametrize('raw_value', ['not-a-number', '-1'])
    def test_parse_cors_options_max_age_invalid_raises(self, session, raw_value: str) -> None:
        '''
        Verify a non-integer or negative max_age value raises ValueError.
        '''

        # Exercise parse_cors_options with an invalid max_age constant.
        with pytest.raises(ValueError):
            session.given(constants={CORS_MAX_AGE_CONST_KEY: raw_value}).run(target=parse_cors_options)

    # * test: unknown_keys_ignored
    def test_parse_cors_options_unknown_keys_ignored(self, session) -> None:
        '''
        Verify unknown constants, including unrecognized cors_* names, are
        ignored rather than raising.
        '''

        # Exercise parse_cors_options with an unrecognized cors_* key alongside a valid one.
        result = session.given(constants={
            'cors_unknown_option': 'anything',
            CORS_ORIGINS_CONST_KEY: 'https://app.example.com',
        }).run(target=parse_cors_options)

        # Assert only the recognized key is reflected.
        assert result == {'origins': ['https://app.example.com']}
