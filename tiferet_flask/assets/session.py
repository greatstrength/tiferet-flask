"""Flask Session Assets

DI service id and flag constants for the Flask session's request-lookup
events, and the stateless handler-closure factories that bind them to a
resolved get_dependency callable (RFP-004 follow-up extraction).
"""

# *** imports

# ** core
from typing import Any, Callable

# *** constants

# ** constant: get_route_evt_service_id
GET_ROUTE_EVT_SERVICE_ID = 'get_route_evt'

# ** constant: get_status_code_evt_service_id
GET_STATUS_CODE_EVT_SERVICE_ID = 'get_status_code_evt'

# ** constant: get_routers_evt_service_id
GET_ROUTERS_EVT_SERVICE_ID = 'get_routers_evt'

# ** constant: app_flag
APP_FLAG = 'app'

# *** functions

# ** function: get_route_handler
def get_route_handler(get_dependency: Callable) -> Callable:
    '''
    Build a route-lookup closure that resolves the get-route event via DI.

    :param get_dependency: The DI resolution handler.
    :type get_dependency: Callable
    :return: A callable that retrieves a route by endpoint.
    :rtype: Callable
    '''

    # Return the handler closure bound to the resolver.
    def handler(**kwargs) -> Any:

        # Resolve and execute the get-route event.
        get_route_evt = get_dependency(GET_ROUTE_EVT_SERVICE_ID, APP_FLAG)
        return get_route_evt.execute(**kwargs)

    # Return the closure.
    return handler

# ** function: get_status_code_handler
def get_status_code_handler(get_dependency: Callable) -> Callable:
    '''
    Build a status-code-lookup closure that resolves the get-status-code event via DI.

    :param get_dependency: The DI resolution handler.
    :type get_dependency: Callable
    :return: A callable that retrieves an HTTP status code by error code.
    :rtype: Callable
    '''

    # Return the handler closure bound to the resolver.
    def handler(**kwargs) -> Any:

        # Resolve and execute the get-status-code event.
        get_status_code_evt = get_dependency(GET_STATUS_CODE_EVT_SERVICE_ID, APP_FLAG)
        return get_status_code_evt.execute(**kwargs)

    # Return the closure.
    return handler

# ** function: get_routers_handler
def get_routers_handler(get_dependency: Callable) -> Callable:
    '''
    Build a routers-lookup closure that resolves the get-routers event via DI.

    :param get_dependency: The DI resolution handler.
    :type get_dependency: Callable
    :return: A callable that retrieves the configured routers.
    :rtype: Callable
    '''

    # Return the handler closure bound to the resolver.
    def handler(**kwargs) -> Any:

        # Resolve and execute the get-routers event.
        get_routers_evt = get_dependency(GET_ROUTERS_EVT_SERVICE_ID, APP_FLAG)
        return get_routers_evt.execute(**kwargs)

    # Return the closure.
    return handler
