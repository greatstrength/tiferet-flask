# *** imports

# ** infra
import pytest
from tiferet import (
    DomainObject,
    StringType
)

# ** app
from ..request import FlaskRequestContext

# *** fixtures

# ** fixture: request_context
@pytest.fixture
def request_context() -> FlaskRequestContext:
    '''
    Fixture to provide a FlaskRequestContext for testing.

    :return: A FlaskRequestContext instance.
    :rtype: FlaskRequestContext
    '''

    # Create a FlaskRequestContext.
    request_context = FlaskRequestContext(
        data=dict(
            key='value',
            another_key='another_value'
        ),
        headers=dict(
            interface_id='test_interface',
        ),
        feature_id='test_group.test_feature'
    )

    # Return the FlaskRequestContext.
    return request_context

# *** tests

# ** test: request_context_handle_response_none
def test_request_context_handle_response_none(request_context: FlaskRequestContext):
    '''
    Test handling a response that is None.

    :param request_context: The FlaskRequestContext instance.
    :type request_context: FlaskRequestContext
    '''

    # Set the request context result to None.
    request_context.set_result(None)

    # Handle a None response.
    response = request_context.handle_response()

    # Check that the response is empty string.
    assert response == ''

# ** test: request_context_handle_response_primitive
def test_request_context_handle_response_primitive(request_context: FlaskRequestContext):
    '''
    Test handling a response that is a primitive type.

    :param request_context: The FlaskRequestContext instance.
    :type request_context: FlaskRequestContext
    '''

    # Set the request context result to a primitive type.
    request_context.set_result('test_string')

    # Handle the response with a primitive type.
    response = request_context.handle_response()

    # Check that the response is as expected.
    assert response == 'test_string'

# ** test: request_context_handle_response_data
def test_request_context_handle_response_data(request_context: FlaskRequestContext):
    '''
    Test handling a response with dict data.

    :param request_context: The FlaskRequestContext instance.
    :type request_context: FlaskRequestContext
    '''

    # Set the request context result to some data.
    request_context.result = {'key': 'value'}

    # Handle the response with data.
    response = request_context.handle_response()

    # Check that the response is as expected.
    assert response == {'key': 'value'}

# ** test: request_context_handle_response_domain_object
def test_request_context_handle_response_domain_object(request_context: FlaskRequestContext):
    '''
    Test handling a response that is a DomainObject.

    :param request_context: The FlaskRequestContext instance.
    :type request_context: FlaskRequestContext
    '''

    # Create a DomainObject to simulate a response.
    class Data(DomainObject):

        key = StringType(
            default='default_value',
            required=True
        )

    # Set the request context result to a DomainObject.
    request_context.set_result(DomainObject.new(Data, key='value'))

    # Handle the response with a DomainObject.
    response = request_context.handle_response()

    # Check that the response is a dict with expected data.
    assert isinstance(response, dict)
    assert response.get('key') == 'value'

# ** test: request_context_handle_response_list
def test_request_context_handle_response_list(request_context: FlaskRequestContext):
    '''
    Test handling a response that is a plain list.

    :param request_context: The FlaskRequestContext instance.
    :type request_context: FlaskRequestContext
    '''

    # Set the request context result to a list.
    request_context.result = ['item1', 'item2', 'item3']

    # Handle the response with a list.
    response = request_context.handle_response()

    # Check that the response is a list and has the expected items.
    assert isinstance(response, list)
    assert response == ['item1', 'item2', 'item3']

# ** test: request_context_handle_response_domain_object_list
def test_request_context_handle_response_domain_object_list(request_context: FlaskRequestContext):
    '''
    Test handling a response that is a list of DomainObjects.

    :param request_context: The FlaskRequestContext instance.
    :type request_context: FlaskRequestContext
    '''

    # Create a DomainObject to simulate a response.
    class Item(DomainObject):

        name = StringType(
            default='default_name',
            required=True
        )

    # Set the request context result to a list of DomainObjects.
    request_context.set_result([
        DomainObject.new(Item, name='item1'),
        DomainObject.new(Item, name='item2')
    ])

    # Handle the response with a list of DomainObjects.
    response = request_context.handle_response()

    # Check that the response is a list of dicts.
    assert isinstance(response, list)
    assert len(response) == 2
    assert response[0].get('name') == 'item1'
    assert response[1].get('name') == 'item2'

# ** test: request_context_handle_response_domain_object_dict
def test_request_context_handle_response_domain_object_dict(request_context: FlaskRequestContext):
    '''
    Test handling a response that is a dict of DomainObjects.

    :param request_context: The FlaskRequestContext instance.
    :type request_context: FlaskRequestContext
    '''

    # Create a DomainObject to simulate a response.
    class Item(DomainObject):

        name = StringType(
            default='default_name',
            required=True
        )

    # Set the request context result to a dict of DomainObjects.
    request_context.set_result({
        'item1': DomainObject.new(Item, name='item1'),
        'item2': DomainObject.new(Item, name='item2')
    })

    # Handle the response with a dict of DomainObjects.
    response = request_context.handle_response()

    # Check that the response is a dict of dicts.
    assert isinstance(response, dict)
    assert len(response) == 2
    assert response['item1'].get('name') == 'item1'
    assert response['item2'].get('name') == 'item2'
