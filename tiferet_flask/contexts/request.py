# *** imports

# ** core
from typing import Any

# ** infra
from tiferet.contexts.request import RequestContext
from tiferet.models import ModelObject

# *** contexts

# ** context: flask_request_context
class FlaskRequestContext(RequestContext):
    '''
    A context for managing Flask request interactions within the Tiferet framework.
    '''
    
    # * method: handle_response
    def handle_response(self) -> Any:
        '''
        Handle the Flask response object.

        :return: The raw data for a Flask response object.
        '''

        # If the response is None, return an empty response.
        if self.result is None:
            return ''
        
        # Convert the response to a dictionary if it's a ModelObject.
        if isinstance(self.result, ModelObject):
            return self.result.to_primitive()
        
        # If the response is a list containing model objects, convert each to a dictionary.
        if isinstance(self.result, list) and all(isinstance(item, ModelObject) for item in self.result):
            return [item.to_primitive() for item in self.result]
        
        # Return the result as JSON with the specified status code.
        return self.result