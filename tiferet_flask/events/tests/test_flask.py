# *** imports

# ** infra
import pytest
from unittest import mock
from tiferet import DomainObject, TiferetError
from tiferet.events import DomainEvent

# ** app
from ..flask import (
    GetFlaskBlueprints,
    GetFlaskRoute,
    GetFlaskStatusCode
)
from ...interfaces import FlaskApiService
from ...mappers import (
    FlaskBlueprintAggregate,
    FlaskRouteAggregate
)

# *** fixtures

# ** fixture: sample_route
@pytest.fixture
def sample_route() -> FlaskRouteAggregate:
    '''
    A sample Flask route aggregate for testing.

    :return: A FlaskRouteAggregate instance.
    :rtype: FlaskRouteAggregate
    '''

    return FlaskRouteAggregate.new(
        id='sample_route',
        rule='/sample',
        methods=['GET', 'POST'],
        status_code=269
    )

# ** fixture: sample_blueprint
@pytest.fixture
def sample_blueprint(sample_route: FlaskRouteAggregate) -> FlaskBlueprintAggregate:
    '''
    A sample Flask blueprint aggregate for testing.

    :param sample_route: A sample route aggregate.
    :type sample_route: FlaskRouteAggregate
    :return: A FlaskBlueprintAggregate instance.
    :rtype: FlaskBlueprintAggregate
    '''

    return FlaskBlueprintAggregate.new(
        name='sample_blueprint',
        routes=[sample_route]
    )

# ** fixture: mock_flask_service
@pytest.fixture
def mock_flask_service(
    sample_blueprint: FlaskBlueprintAggregate,
    sample_route: FlaskRouteAggregate
) -> FlaskApiService:
    '''
    A mock FlaskApiService for testing.

    :param sample_blueprint: A sample blueprint aggregate.
    :type sample_blueprint: FlaskBlueprintAggregate
    :param sample_route: A sample route aggregate.
    :type sample_route: FlaskRouteAggregate
    :return: A mocked FlaskApiService.
    :rtype: FlaskApiService
    '''

    service = mock.Mock(spec=FlaskApiService)
    service.get_blueprints.return_value = [sample_blueprint]
    service.get_route.return_value = sample_route
    service.get_status_code.return_value = 420

    return service

# *** tests

# ** test: get_flask_blueprints_success
def test_get_flask_blueprints_success(
    mock_flask_service: FlaskApiService,
    sample_blueprint: FlaskBlueprintAggregate
) -> None:
    '''
    Test successful retrieval of all Flask blueprints.

    :param mock_flask_service: The mocked Flask API service.
    :type mock_flask_service: FlaskApiService
    :param sample_blueprint: The expected blueprint.
    :type sample_blueprint: FlaskBlueprintAggregate
    '''

    # Execute the event via DomainEvent.handle.
    result = DomainEvent.handle(
        GetFlaskBlueprints,
        dependencies={'flask_service': mock_flask_service},
    )

    # Assert the result.
    assert result == [sample_blueprint]
    mock_flask_service.get_blueprints.assert_called_once()

# ** test: get_flask_route_success
def test_get_flask_route_success(
    mock_flask_service: FlaskApiService,
    sample_route: FlaskRouteAggregate
) -> None:
    '''
    Test successful retrieval of a Flask route with blueprint prefix.

    :param mock_flask_service: The mocked Flask API service.
    :type mock_flask_service: FlaskApiService
    :param sample_route: The expected route.
    :type sample_route: FlaskRouteAggregate
    '''

    # Execute the event via DomainEvent.handle.
    result = DomainEvent.handle(
        GetFlaskRoute,
        dependencies={'flask_service': mock_flask_service},
        endpoint='sample_blueprint.sample_route',
    )

    # Assert the result.
    assert result is sample_route
    mock_flask_service.get_route.assert_called_once_with(
        route_id='sample_route',
        blueprint_name='sample_blueprint',
    )

# ** test: get_flask_route_without_blueprint
def test_get_flask_route_without_blueprint(
    mock_flask_service: FlaskApiService,
    sample_route: FlaskRouteAggregate
) -> None:
    '''
    Test retrieval of a Flask route without blueprint prefix.

    :param mock_flask_service: The mocked Flask API service.
    :type mock_flask_service: FlaskApiService
    :param sample_route: The expected route.
    :type sample_route: FlaskRouteAggregate
    '''

    # Execute the event via DomainEvent.handle.
    result = DomainEvent.handle(
        GetFlaskRoute,
        dependencies={'flask_service': mock_flask_service},
        endpoint='sample_route',
    )

    # Assert the result.
    assert result is sample_route
    mock_flask_service.get_route.assert_called_once_with(
        route_id='sample_route',
        blueprint_name=None,
    )

# ** test: get_flask_route_not_found
def test_get_flask_route_not_found(
    mock_flask_service: FlaskApiService,
) -> None:
    '''
    Test that GetFlaskRoute raises FLASK_ROUTE_NOT_FOUND when route does not exist.

    :param mock_flask_service: The mocked Flask API service.
    :type mock_flask_service: FlaskApiService
    '''

    # Configure the mock to return None.
    mock_flask_service.get_route.return_value = None

    # Execute and assert the error.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            GetFlaskRoute,
            dependencies={'flask_service': mock_flask_service},
            endpoint='nonexistent_route',
        )

    # Assert the error code.
    assert exc_info.value.error_code == 'FLASK_ROUTE_NOT_FOUND'

# ** test: get_flask_route_missing_endpoint
def test_get_flask_route_missing_endpoint(
    mock_flask_service: FlaskApiService,
) -> None:
    '''
    Test that GetFlaskRoute raises an error when endpoint is not provided.

    :param mock_flask_service: The mocked Flask API service.
    :type mock_flask_service: FlaskApiService
    '''

    # Execute without the required endpoint parameter.
    with pytest.raises(TiferetError):
        DomainEvent.handle(
            GetFlaskRoute,
            dependencies={'flask_service': mock_flask_service},
        )

# ** test: get_flask_status_code_success
def test_get_flask_status_code_success(
    mock_flask_service: FlaskApiService,
) -> None:
    '''
    Test successful retrieval of a status code.

    :param mock_flask_service: The mocked Flask API service.
    :type mock_flask_service: FlaskApiService
    '''

    # Execute the event via DomainEvent.handle.
    result = DomainEvent.handle(
        GetFlaskStatusCode,
        dependencies={'flask_service': mock_flask_service},
        error_code='TEST_ERROR',
    )

    # Assert the result.
    assert result == 420
    mock_flask_service.get_status_code.assert_called_once_with(
        error_code='TEST_ERROR'
    )

# ** test: get_flask_status_code_missing_error_code
def test_get_flask_status_code_missing_error_code(
    mock_flask_service: FlaskApiService,
) -> None:
    '''
    Test that GetFlaskStatusCode raises an error when error_code is not provided.

    :param mock_flask_service: The mocked Flask API service.
    :type mock_flask_service: FlaskApiService
    '''

    # Execute without the required error_code parameter.
    with pytest.raises(TiferetError):
        DomainEvent.handle(
            GetFlaskStatusCode,
            dependencies={'flask_service': mock_flask_service},
        )
