'''Tiferet Flask assets.'''

# *** exports

# ** app
from .cors import (
    CORS_ALLOW_HEADERS_CONST_KEY,
    CORS_EXPOSE_HEADERS_CONST_KEY,
    CORS_MAX_AGE_CONST_KEY,
    CORS_METHODS_CONST_KEY,
    CORS_ORIGINS_CONST_KEY,
    CORS_SUPPORTS_CREDENTIALS_CONST_KEY,
    parse_cors_options,
)
