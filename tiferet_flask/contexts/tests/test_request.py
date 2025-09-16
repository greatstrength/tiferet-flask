# *** imports

# ** infra
import pytest
from tiferet import (
    ModelObject,
    StringType
)

# ** app
from ..request import *

# *** fixtures

# ** fixture: request_context
@pytest.fixture
def request_context():
    """Fixture to provide a mock FlaskRequestContext."""

    # Create a mock FlaskRequestContext.
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

    # Return the mock FlaskRequestContext.
    return request_context

# *** tests

# ** test: request_context_handle_response_none
def test_request_context_handle_response_none(request_context):
    """
    Test handling a response that is None in the FlaskRequestContext.

    :param request_context: The FlaskRequestContext instance.
    :type request_context: FlaskRequestContext
    """

    # Set the request context result to None.
    request_context.set_result(None)

    # Handle a None response.
    response = request_context.handle_response()

    # Check that the response is None.
    assert response == ''

# ** test: request_context_handle_response_primitive
def test_request_context_handle_response_primitive(request_context):
    """
    Test handling a response that is a primitive type in the FlaskRequestContext.

    :param request_context: The FlaskRequestContext instance.
    :type request_context: FlaskRequestContext
    """

    # Set the request context result to a primitive type.
    request_context.set_result('test_string')

    # Handle the response with a primitive type.
    response = request_context.handle_response()

    # Check that the response is as expected.
    assert response == 'test_string'

# ** test: request_context_handle_response_data
def test_request_context_handle_response_data(request_context):
    """
    Test handling a response with data in the FlaskRequestContext.

    :param request_context: The FlaskRequestContext instance.
    :type request_context: FlaskRequestContext
    """

    # Set the request context result to some data.
    request_context.result = {'key': 'value'}

    # Handle the response with data.
    response = request_context.handle_response()

    # Check that the response is as expected.
    assert response == {'key': 'value'}

# ** test: request_context_handle_response_model_object
def test_request_context_handle_response_model_object(request_context):
    """
    Test handling a response that is a ModelObject in the FlaskRequestContext.

    :param request_context: The FlaskRequestContext instance.
    :type request_context: FlaskRequestContext
    """

    # Create a ModelObject to simulate a response.
    class Data(ModelObject):

        key = StringType(
            default='default_value',
            required=True
        )

    # Set the request context result to a ModelObject.
    request_context.set_result(ModelObject.new(Data, key='value'))

    # Handle the response with a ModelObject.
    response = request_context.handle_response()

    # Check that the response is a ModelObject and has the expected data.
    assert isinstance(response, dict)
    assert response.get('key') == 'value'

# ** test: request_context_handle_response_list
def test_request_context_handle_response_list(request_context):
    """
    Test handling a response that is a list in the FlaskRequestContext.

    :param request_context: The FlaskRequestContext instance.
    :type request_context: FlaskRequestContext
    """

    # Set the request context result to a list.
    request_context.result = ['item1', 'item2', 'item3']

    # Handle the response with a list.
    response = request_context.handle_response()

    # Check that the response is a list and has the expected items.
    assert isinstance(response, list)
    assert response == ['item1', 'item2', 'item3']

# ** test: request_context_handle_response_model_list
def test_request_context_handle_response_model_list(request_context):
    """
    Test handling a response that is a list of ModelObjects in the FlaskRequestContext.

    :param request_context: The FlaskRequestContext instance.
    :type request_context: FlaskRequestContext
    """

    # Create a ModelObject to simulate a response.
    class Item(ModelObject):

        name = StringType(
            default='default_name',
            required=True
        )

    # Set the request context result to a list of ModelObjects.
    request_context.set_result([
        ModelObject.new(Item, name='item1'),
        ModelObject.new(Item, name='item2')
    ])

    # Handle the response with a list of ModelObjects.
    response = request_context.handle_response()

    # Check that the response is a list and contains ModelObjects with expected names.
    assert isinstance(response, list)
    assert len(response) == 2
    assert response[0].get('name') == 'item1'
    assert response[1].get('name') == 'item2'

# ** test: request_context_handle_response_model_dict
def test_request_context_handle_response_model_dict(request_context):
    """
    Test handling a response that is a dict of ModelObjects in the FlaskRequestContext.

    :param request_context: The FlaskRequestContext instance.
    :type request_context: FlaskRequestContext
    """

    # Create a ModelObject to simulate a response.
    class Item(ModelObject):

        name = StringType(
            default='default_name',
            required=True
        )

    # Set the request context result to a dict of ModelObjects.
    request_context.set_result({
        'item1': ModelObject.new(Item, name='item1'),
        'item2': ModelObject.new(Item, name='item2')
    })

    # Handle the response with a dict of ModelObjects.
    response = request_context.handle_response()

    # Check that the response is a dict and contains ModelObjects with expected names.
    assert isinstance(response, dict)
    assert len(response) == 2
    assert response['item1'].get('name') == 'item1'
    assert response['item2'].get('name') == 'item2'