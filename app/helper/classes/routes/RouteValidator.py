"""
Defines the RouteValidator class.

This class is a helper for the RouteInitialiser. Its sole purpose is
to validate all components of a route (rule, endpoint, methods, etc.)
and a blueprint *before* they are registered with the Flask app.

It is a stateful class that maintains sets of all registered endpoints
and blueprint names to prevent duplicates.
"""

from flask import Blueprint
from typing import Mapping, Any, Optional, Tuple

class RouteValidator():
    """
    A stateful class that validates routes and blueprints before registration.
    
    This class maintains sets of registered endpoint and blueprint names
    at the class level to prevent duplicates across the application's lifetime,
    which would otherwise cause a runtime error in Flask.
    """
    
    # Type hint for the Flask route specification
    _ViewSpec = Mapping[str, Any]
    
    # A set of all allowed HTTP methods
    _methods_list: set = {"GET", "POST", "PATCH", "PUT", "DELETE"}
    
    # --- Stateful Class Attributes ---
    # These sets are modified by the validation methods to track
    # what has already been registered.
    _endpoint_list: set = set()
    _blueprint_set: set = set()

    def __init__(self) -> None:
        """
        Initializes the RouteValidator.
        
        Note: The state (endpoint and blueprint sets) is stored
        at the class level, not the instance level.
        """
        pass

    def validate_rule(self, rule) -> Tuple[bool, Optional[Exception]]:
        """
        Validates a route's URL rule.

        Checks:
        1. Is the rule a string?
        2. Does the rule start with a '/'?

        Args:
            rule (any): The URL rule string to validate (e.g., "/home").

        Returns:
            Tuple[bool, Optional[Exception]]: (True, None) on success,
            or (False, Exception) on failure.
        """
        if not isinstance(rule, str):
            return (False, TypeError(f"Invalid rule type: {type(rule)}"))

        if not rule.startswith('/'):
            return (False, ValueError(f"Rule must start with '/'. Rule: {rule!r}"))
        
        return (True, None)

    def validate_endpoint(self, endpoint) -> Tuple[bool, Optional[Exception]]:
        """
        Validates a route's endpoint name.

        Checks:
        1. Is the endpoint a string?
        2. Is this endpoint name a duplicate of one already registered?

        If valid, it adds the endpoint to the class-level '_endpoint_list' set.

        Args:
            endpoint (any): The endpoint name to validate (e.g., "app.home").

        Returns:
            Tuple[bool, Optional[Exception]]: (True, None) on success,
            or (False, Exception) on failure.
        """
        if not isinstance(endpoint, str):
            return (False, ValueError(f"Invalid endpoint: {endpoint!r}"))

        elif endpoint in self._endpoint_list:
            return (False, ValueError(f"Duplicate endpoint: {endpoint}"))

        # Add the new, valid endpoint to the set to track it
        self._endpoint_list.add(endpoint)
        return (True, None)
    
    def validate_methods(self, methods) -> Tuple[bool, Optional[Exception]]:
        """
        Validates a route's list of HTTP methods.

        Checks:
        1. Are all methods in the list (e.g., "GET", "POST") valid
           HTTP methods recognized by this validator?

        Args:
            methods (list[str]): A list of HTTP method strings.

        Returns:
            Tuple[bool, Optional[Exception]]: (True, None) on success,
            or (False, Exception) on failure.
        """
        # Check if all provided methods are in our master list
        if not all([method.upper() in self._methods_list for method in methods]):
            return (False, ValueError(f"Invalid method given {methods=}"))

        return (True, None)

    def validate_blueprint(self, blueprint) -> Tuple[bool, Optional[Exception]]:
        """
        Validates a Flask Blueprint object.

        Checks:
        1. Is the object a genuine Flask Blueprint instance?
        2. Is this blueprint name a duplicate of one already registered?

        If valid, it adds the blueprint's name to the
        class-level '_blueprint_set'.

        Args:
            blueprint (any): The Blueprint object to validate.

        Returns:
            Tuple[bool, Optional[Exception]]: (True, None) on success,
            or (False, Exception) on failure.
        """
        # A 'None' blueprint is valid (e.g., for the 'index' route)
        if not blueprint:
            return (True, None)

        if not isinstance(blueprint, Blueprint):
            return (False, TypeError(f"Invalid blueprint type: {type(blueprint)}"))

        elif blueprint.name in self._blueprint_set:
            return (False, ValueError(f"Duplicate blueprint {blueprint.name}"))
        
        # Add the new, valid blueprint name to the set to track it
        self._blueprint_set.add(blueprint.name)

        return (True, None)

    def validate_func(self, func) -> Tuple[bool, Optional[Exception]]:
        """
        Validates a route's view function.

        Checks:
        1. Is the provided 'func' a callable function?

        Args:
            func (any): The view function to validate.

        Returns:
            Tuple[bool, Optional[Exception]]: (True, None) on success,
            or (False, Exception) on failure.
        """
        if not callable(func):
            return (False, TypeError(f"View function must be a callable function: {func!r}"))

        return (True, None)