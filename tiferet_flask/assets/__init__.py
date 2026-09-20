"""Flask Assets."""

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
from .session import (
    APP_FLAG,
    GET_ROUTE_EVT_SERVICE_ID,
    GET_ROUTERS_EVT_SERVICE_ID,
    GET_STATUS_CODE_EVT_SERVICE_ID,
    get_route_handler,
    get_routers_handler,
    get_status_code_handler,
)
