# *** imports

# ** core
from typing import Any, Tuple

# ** infra
from tiferet.models import IntegerType
from tiferet.models.error import Error
from flask import jsonify

# *** models

# ** model: flask_error
class FlaskError(Error):
    '''
    A model representing errors specific to Flask API operations.
    '''

    # * attribute: status_code
    status_code = IntegerType(
        required=True,
        default=400,
        metadata=dict(
            description='The HTTP status code associated with the error.'
        )
    )

    # * method: format_response
    def format_response(self, lang = 'en_US', *args, **kwargs) -> Tuple[Any, int]:
        '''
        Format the error response for Flask.
        
        :param lang: The language code for the error message.
        :type lang: str
        :param args: Additional arguments for formatting the error message.
        :type args: tuple
        :param kwargs: Additional keyword arguments for formatting the error message.
        :type kwargs: dict
        :return: A Flask JSON response containing the error details.
        :rtype: Any
        '''

        # Return a JSON response with the appropriate status code.
        return super().format_response(lang, *args, **kwargs), self.status_code