from flask import Blueprint
from typing import Mapping, Any, Optional, Tuple

class BaseValidator():
    _ViewSpec = Mapping[str, Any]
    _methods_list = {"GET", "POST", "PATCH", "PUT", "DELETE"}
    _endpoint_list = set()
    _blueprint_set = set()

    def __init__(self) -> None:
        pass

    # Rule Validation
    def validate_rule(self, rule) -> Tuple[bool, Optional[Exception]]:
        # check for a type or value error
        if not isinstance(rule, str):
            return (False, TypeError(f"Invalid rule type: {type(rule)}"))

        if not rule.startswith('/'):
            return (False, ValueError(f"Rule must start with '/'. Rule: {rule!r}"))
        
        return (True, None)

    # Endpoint Validation
    def validate_endpoint(self, endpoint) -> Tuple[bool, Optional[Exception]]:
        # Check for a type or value error
        if not isinstance(endpoint, str):
            return (False, ValueError(f"Invalid endpoint: {endpoint!r}"))

        elif endpoint in self._endpoint_list:
            return (False, ValueError(f"Duplicate endpoint: {endpoint}"))

        # Add the endpoint to the set
        self._endpoint_list.add(endpoint)
        return (True, None)
    
    def validate_methods(self, methods) -> Tuple[bool, Optional[Exception]]:
        # Check if a method is invalid
        if not all([method.upper() in self._methods_list for method in methods]):
            return (False, ValueError(f"Invalid method given {methods=}"))

        return (True, None)

    def validate_blueprint(self, blueprint) -> Tuple[bool, Optional[Exception]]:
        # If blueprint is none, skip
        if not blueprint:
            return (True, None)

        # Change values if an error exists
        if not isinstance(blueprint, Blueprint):
            return (False, TypeError(f"Invalid blueprint type: {type(blueprint)}"))

        elif blueprint.name in self._blueprint_set:
            return (False, ValueError(f"Duplicate blueprint {blueprint.name}"))
        
        # Add the blueprint to the set
        self._blueprint_set.add(blueprint.name)

        return (True, None)

    def validate_func(self, func) -> Tuple[bool, Optional[Exception]]:
        # check the function is callable
        if not callable(func):
            return (False, TypeError(f"View function must be a callable function: {func!r}"))

        return (True, None)
