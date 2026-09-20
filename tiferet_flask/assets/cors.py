'''Flask CORS AppSession Constants

This module holds the closed ``cors_*`` AppSession constant key names and the
stateless parsers that translate them into ``flask_cors.CORS`` kwargs.
'''

# *** imports

# ** core
from typing import Any, Dict

# *** constants

# ** constant: cors_origins_const_key
CORS_ORIGINS_CONST_KEY = 'cors_origins'

# ** constant: cors_methods_const_key
CORS_METHODS_CONST_KEY = 'cors_methods'

# ** constant: cors_allow_headers_const_key
CORS_ALLOW_HEADERS_CONST_KEY = 'cors_allow_headers'

# ** constant: cors_expose_headers_const_key
CORS_EXPOSE_HEADERS_CONST_KEY = 'cors_expose_headers'

# ** constant: cors_supports_credentials_const_key
CORS_SUPPORTS_CREDENTIALS_CONST_KEY = 'cors_supports_credentials'

# ** constant: cors_max_age_const_key
CORS_MAX_AGE_CONST_KEY = 'cors_max_age'

# ** constant: cors_list_option_map
CORS_LIST_OPTION_MAP = {
    CORS_ORIGINS_CONST_KEY: 'origins',
    CORS_METHODS_CONST_KEY: 'methods',
    CORS_ALLOW_HEADERS_CONST_KEY: 'allow_headers',
    CORS_EXPOSE_HEADERS_CONST_KEY: 'expose_headers',
}

# ** constant: cors_true_values
CORS_TRUE_VALUES = (
    'true',
    '1',
    'yes',
)

# ** constant: cors_false_values
CORS_FALSE_VALUES = (
    'false',
    '0',
    'no',
)

# *** functions

# ** function: parse_cors_list_option
def parse_cors_list_option(raw_value: str) -> Any:
    '''
    Parse a comma-separated constant string into a flask-cors list or wildcard value.

    :param raw_value: The raw AppSession constant string.
    :type raw_value: str
    :return: ``'*'`` for a lone wildcard, a token list, or ``None`` when absent.
    :rtype: Any
    '''

    # Split the raw value into stripped tokens, dropping empties.
    tokens = [token.strip() for token in raw_value.split(',') if token.strip()]

    # Treat a fully empty token list as an absent option.
    if not tokens:
        return None

    # Return flask-cors wildcard form for a lone asterisk.
    if tokens == ['*']:
        return '*'

    # Return the remaining tokens in original order.
    return tokens

# ** function: parse_cors_bool_option
def parse_cors_bool_option(const_key: str, raw_value: str) -> bool:
    '''
    Parse a case-insensitive boolean constant string.

    :param const_key: The AppSession constant key name.
    :type const_key: str
    :param raw_value: The raw AppSession constant string.
    :type raw_value: str
    :return: The parsed boolean value.
    :rtype: bool
    :raises ValueError: If ``raw_value`` is not a recognized boolean token.
    '''

    # Normalize the raw value for case-insensitive membership.
    normalized = raw_value.strip().lower()

    # Return True when the normalized value is a true token.
    if normalized in CORS_TRUE_VALUES:
        return True

    # Return False when the normalized value is a false token.
    if normalized in CORS_FALSE_VALUES:
        return False

    # Reject unrecognized boolean tokens with the original raw value.
    raise ValueError(
        f'Invalid boolean value for constant {const_key!r}: {raw_value!r}'
    )

# ** function: parse_cors_max_age_option
def parse_cors_max_age_option(const_key: str, raw_value: str) -> int:
    '''
    Parse a non-negative integer constant string.

    :param const_key: The AppSession constant key name.
    :type const_key: str
    :param raw_value: The raw AppSession constant string.
    :type raw_value: str
    :return: The parsed non-negative integer.
    :rtype: int
    :raises ValueError: If ``raw_value`` is not a non-negative integer.
    '''

    # Parse a non-negative integer, chaining any conversion failure.
    try:

        # Parse the raw value as an integer.
        max_age = int(raw_value)

        # Reject negative integers as invalid.
        if max_age < 0:
            raise ValueError(raw_value)
    except (TypeError, ValueError) as exception:
        raise ValueError(
            f'Invalid non-negative integer for constant {const_key!r}: {raw_value!r}'
        ) from exception

    # Return the parsed max age.
    return max_age

# ** function: parse_cors_options
def parse_cors_options(constants: Dict[str, str]) -> dict:
    '''
    Parse the closed ``cors_*`` session constants into flask-cors kwargs.

    Empty dict when no recognized keys are set.

    :param constants: The resolved AppSession constants map.
    :type constants: Dict[str, str]
    :return: flask-cors kwargs, or an empty dict when no recognized keys are set.
    :rtype: dict
    '''

    # Start with an empty flask-cors kwargs dict.
    options = {}

    # Parse recognized list-valued CORS constants.
    for const_key, kwarg_name in CORS_LIST_OPTION_MAP.items():

        # Skip missing or falsy raw values.
        raw_value = constants.get(const_key)
        if not raw_value:
            continue

        # Omit the kwarg when the helper treats the value as absent.
        parsed_value = parse_cors_list_option(raw_value)
        if parsed_value is None:
            continue

        # Set the flask-cors list kwarg.
        options[kwarg_name] = parsed_value

    # Parse credentials when the session constant is present.
    raw_credentials = constants.get(CORS_SUPPORTS_CREDENTIALS_CONST_KEY)
    if raw_credentials is not None:
        options['supports_credentials'] = parse_cors_bool_option(
            CORS_SUPPORTS_CREDENTIALS_CONST_KEY,
            raw_credentials,
        )

    # Parse max age when the session constant is present.
    raw_max_age = constants.get(CORS_MAX_AGE_CONST_KEY)
    if raw_max_age is not None:
        options['max_age'] = parse_cors_max_age_option(
            CORS_MAX_AGE_CONST_KEY,
            raw_max_age,
        )

    # Return the assembled flask-cors kwargs.
    return options
