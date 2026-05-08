# *** imports

# ** infra
import pytest
from pydantic import BaseModel, Field

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

    return FlaskRequestContext(
        data=dict(
            key='value',
            another_key='another_value',
        ),
        headers=dict(
            interface_id='test_interface',
        ),
        feature_id='test_group.test_feature',
    )

# *** tests

# ** test: request_context_handle_response_none
def test_request_context_handle_response_none(request_context: FlaskRequestContext):
    '''
    Test handling a response that is None.
    '''

    request_context.set_result(None)
    response = request_context.handle_response()
    assert response == ''

# ** test: request_context_handle_response_primitive
def test_request_context_handle_response_primitive(request_context: FlaskRequestContext):
    '''
    Test handling a response that is a primitive type.
    '''

    request_context.set_result('test_string')
    response = request_context.handle_response()
    assert response == 'test_string'

# ** test: request_context_handle_response_data
def test_request_context_handle_response_data(request_context: FlaskRequestContext):
    '''
    Test handling a response with dict data.
    '''

    request_context.result = {'key': 'value'}
    response = request_context.handle_response()
    assert response == {'key': 'value'}

# ** test: request_context_handle_response_base_model
def test_request_context_handle_response_base_model(request_context: FlaskRequestContext):
    '''
    Test handling a response that is a BaseModel.
    '''

    # Create a BaseModel subclass to simulate a response.
    class Data(BaseModel):
        key: str = Field(default='default_value')

    # Set the request context result to a BaseModel.
    request_context.set_result(Data(key='value'))

    # Handle the response.
    response = request_context.handle_response()

    # Check that the response is a dict with expected data.
    assert isinstance(response, dict)
    assert response.get('key') == 'value'

# ** test: request_context_handle_response_list
def test_request_context_handle_response_list(request_context: FlaskRequestContext):
    '''
    Test handling a response that is a plain list.
    '''

    request_context.result = ['item1', 'item2', 'item3']
    response = request_context.handle_response()
    assert isinstance(response, list)
    assert response == ['item1', 'item2', 'item3']

# ** test: request_context_handle_response_base_model_list
def test_request_context_handle_response_base_model_list(request_context: FlaskRequestContext):
    '''
    Test handling a response that is a list of BaseModel instances.
    '''

    # Create a BaseModel subclass.
    class Item(BaseModel):
        name: str = Field(default='default_name')

    # Set the result to a list of BaseModel instances.
    request_context.set_result([
        Item(name='item1'),
        Item(name='item2'),
    ])

    # Handle the response.
    response = request_context.handle_response()

    # Check the response.
    assert isinstance(response, list)
    assert len(response) == 2
    assert response[0].get('name') == 'item1'
    assert response[1].get('name') == 'item2'

# ** test: request_context_set_result_with_data_key
def test_request_context_set_result_with_data_key(request_context: FlaskRequestContext):
    '''
    Test that set_result with a data_key delegates to the parent method.
    '''

    request_context.set_result('intermediate_value', data_key='step_result')
    assert request_context.data['step_result'] == 'intermediate_value'
    assert request_context.result is None

# ** test: request_context_handle_response_base_model_dict
def test_request_context_handle_response_base_model_dict(request_context: FlaskRequestContext):
    '''
    Test handling a response that is a dict of BaseModel instances.
    '''

    # Create a BaseModel subclass.
    class Item(BaseModel):
        name: str = Field(default='default_name')

    # Set the result to a dict of BaseModel instances.
    request_context.set_result({
        'item1': Item(name='item1'),
        'item2': Item(name='item2'),
    })

    # Handle the response.
    response = request_context.handle_response()

    # Check the response.
    assert isinstance(response, dict)
    assert len(response) == 2
    assert response['item1'].get('name') == 'item1'
    assert response['item2'].get('name') == 'item2'
