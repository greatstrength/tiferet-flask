"""Flask CORS Assets

Closed cors_* AppSession constant key names and the stateless parsing
functions that translate them into flask_cors.CORS kwargs (RFP-004).
"""

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
    Parse a comma-separated constant string into a flask-cors list/wildcard value.

    :param raw_value: The raw comma-separated constant value.
    :type raw_value: str
    :return: The wildcard string '*', a list of tokens, or None when empty.
    :rtype: Any
    '''

    # Split on commas, strip whitespace, and drop empty tokens.
    tokens = [token.strip() for token in raw_value.split(',') if token.strip()]

    # Treat an empty token list as absent.
    if not tokens:
        return None

    # Preserve flask-cors' wildcard string form for a lone '*' token.
    if tokens == ['*']:
        return '*'

    # Return the parsed token list.
    return tokens

# ** function: parse_cors_bool_option
def parse_cors_bool_option(const_key: str, raw_value: str) -> bool:
    '''
    Parse a case-insensitive boolean constant string.

    :param const_key: The constant key being parsed, for error reporting.
    :type const_key: str
    :param raw_value: The raw constant value.
    :type raw_value: str
    :return: The parsed boolean.
    :rtype: bool
    :raises ValueError: If raw_value is not a recognized boolean token.
    '''

    # Normalize the raw value for case-insensitive comparison.
    normalized_value = raw_value.strip().lower()

    # Match against the recognized true/false token sets.
    if normalized_value in CORS_TRUE_VALUES:
        return True
    if normalized_value in CORS_FALSE_VALUES:
        return False

    # Raise if the value is not a recognized boolean token.
    raise ValueError(f'Invalid boolean value for constant {const_key!r}: {raw_value!r}')

# ** function: parse_cors_max_age_option
def parse_cors_max_age_option(const_key: str, raw_value: str) -> int:
    '''
    Parse a non-negative integer constant string.

    :param const_key: The constant key being parsed, for error reporting.
    :type const_key: str
    :param raw_value: The raw constant value.
    :type raw_value: str
    :return: The parsed non-negative integer.
    :rtype: int
    :raises ValueError: If raw_value is not a non-negative integer.
    '''

    # Attempt to parse the value as an integer, rejecting negatives.
    try:
        parsed_value = int(raw_value)
        if parsed_value < 0:
            raise ValueError
    except (TypeError, ValueError) as exception:
        raise ValueError(f'Invalid non-negative integer for constant {const_key!r}: {raw_value!r}') from exception

    # Return the parsed value.
    return parsed_value

# ** function: parse_cors_options
def parse_cors_options(constants: Dict[str, str]) -> dict:
    '''
    Parse the closed set of cors_* session constants into flask-cors kwargs.

    :param constants: The resolved AppSession constants map.
    :type constants: Dict[str, str]
    :return: A kwargs dict suitable for flask_cors.CORS(**options); empty when
        no recognized keys are set (today's wide-open default applies).
    :rtype: dict
    '''

    # Accumulate recognized options; unknown keys are ignored.
    options = {}

    # Parse the four comma-separated list options.
    for const_key, kwarg_name in CORS_LIST_OPTION_MAP.items():
        raw_value = constants.get(const_key)
        if not raw_value:
            continue
        parsed_value = parse_cors_list_option(raw_value)
        if parsed_value is not None:
            options[kwarg_name] = parsed_value

    # Parse the boolean supports_credentials option.
    raw_supports_credentials = constants.get(CORS_SUPPORTS_CREDENTIALS_CONST_KEY)
    if raw_supports_credentials is not None:
        options['supports_credentials'] = parse_cors_bool_option(
            CORS_SUPPORTS_CREDENTIALS_CONST_KEY,
            raw_supports_credentials,
        )

    # Parse the integer max_age option.
    raw_max_age = constants.get(CORS_MAX_AGE_CONST_KEY)
    if raw_max_age is not None:
        options['max_age'] = parse_cors_max_age_option(CORS_MAX_AGE_CONST_KEY, raw_max_age)

    # Return the parsed CORS kwargs.
    return options
