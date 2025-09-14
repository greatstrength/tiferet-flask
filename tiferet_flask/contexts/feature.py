# *** imports

# ** infra
from tiferet.contexts.feature import (
    FeatureContext,
    ContainerContext,
    CacheContext,
    RequestContext,
    raise_error,
    parse_parameter
)
from tiferet.handlers.feature import FeatureHandler
from tiferet.models.feature import (
    FeatureCommand
)
from tiferet.commands import Command

# ** app
from ..models.feature import FlaskFeature

# *** contexts

# ** context: flask_feature_context
class FlaskFeatureContext(FeatureContext):
    '''
    A context for managing Flask feature handling within the Tiferet framework.
    '''
    
    feature_handler: FeatureHandler

    # * init
    def __init__(self, feature_handler: FeatureHandler, container: ContainerContext, cache_context: CacheContext = None):
        '''
        Initialize the feature context with the given feature handler.

        :param feature_handler: An instance of FeatureHandler.
        :type feature_handler: FeatureHandler
        :param container: The container context for dependency injection.
        :type container: ContainerContext
        :param cache_context: The cache context to use for caching feature data.
        :type cache_context: CacheContext
        '''

        # Set the feature handler.
        self.feature_handler = feature_handler

        # Initialize the base FeatureContext with the provided handler.
        super().__init__(
            feature_service=feature_handler, 
            container=container, 
            cache=cache_context
        )

    # * method: load_feature
    def load_feature(self, feature_id: str) -> FlaskFeature:
        '''
        Retrieve a FlaskFeature by its feature ID.

        :param feature_id: The feature ID to look up.
        :type feature_id: str
        :return: The corresponding FlaskFeature instance.
        :rtype: FlaskFeature
        '''
        
        # Try to get the feature by its id from the cache.
        # If it does not exist, retrieve it from the feature handler and cache it.
        feature = self.cache.get(feature_id)
        if not feature:
            feature = self.feature_service.get_feature(feature_id)
            self.cache.set(feature_id, feature)

        # Return the feature.
        return feature
            
    # * method: parse_parameter
    def parse_parameter(self, parameter: str, request: RequestContext = None) -> str:
        '''
        Parse a parameter.

        :param parameter: The parameter to parse.
        :type parameter: str:
        param request: The request object containing data for parameter parsing.
        :type request: Request
        :return: The parsed parameter.
        :rtype: str
        '''

        # Parse the parameter if it not a request parameter.
        if not parameter.startswith('$r.'):
            return parse_parameter.execute(parameter)
        
        # Raise an error if the request is and the parameter comes from the request.
        if not request and parameter.startswith('$r.'):
            raise_error.execute(
                'REQUEST_NOT_FOUND',
                'Request data is not available for parameter parsing.',
                parameter
            )
    
        # Parse the parameter from the request if provided.
        result = request.data.get(parameter[3:], None)
        
        # Raise an error if the parameter is not found in the request data.
        if result is None:
            raise_error.execute(
                'PARAMETER_NOT_FOUND',
                f'Parameter {parameter} not found in request data.',
                parameter
            )

        # Return the parsed parameter.
        return result

    # * method: handle_feature_command
    def handle_feature_command(self,
        command: Command,
        request: RequestContext,
        feature_command: FeatureCommand,
        **kwargs
    ):
        '''
        Handle the execution of a feature command with the provided request and command-handling options.
        :param command: The command to execute.
        :type command: Command
        :param request: The request context object.
        :type request: RequestContext
        :param feature_command: The feature command metadata.
        :type feature_command: FeatureCommand
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Handle the command with the request and feature command options.
        # NOTE: The  method executed is to be obsoleted, and this to be consolidated with handle_command for v2.
        self.handle_command(
            command,
            request,
            data_key=feature_command.data_key,
            pass_on_error=feature_command.pass_on_error,
            **{id: self.parse_parameter(param, request) for id, param in feature_command.parameters.items()},
            **kwargs
        )
    
    # * method: execute_feature
    def execute_feature(self, feature_id: str, request: RequestContext, **kwargs):
        '''
        Execute a feature by its ID with the provided request.
        
        :param request: The request context object.
        :type request: RequestContext
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Load the feature by its ID.
        feature = self.load_feature(feature_id)

        # Load the command dependencies from the container for the feature.
        commands = [
            self.load_feature_command(cmd.attribute_id)
            for cmd in feature.commands
        ]
              
        # Execute each command in the feature with the request and feature command options.
        for index, command in enumerate(commands):
            self.handle_feature_command(
                command=command,
                request=request,
                feature_command=feature.commands[index],
                features=self.feature_service,
                container=self.container,
                cache=self.cache,
                **kwargs
            )

        # Update the request result with the feature result and status code if available.
        request.result = (request.result, feature.status_code)