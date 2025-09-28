from typing import Mapping, Iterable
from .validation import BaseValidator
from flask import Flask

class RouteRegistrar():
    _validator = None
    _app = None

    def __init__(self, app: Flask, validator: BaseValidator) -> None:
        if validator is None:
            raise TypeError(f"Validator not provided. Add a validator to ensure routes are correctly validated {validator=}")
        
        if app is None:
            raise TypeError(f"App not provided. App required to attach routes to. {app=}")

        self._app = app
        self._validator = validator

    def add_blueprint(self, route_spec) -> bool:
        blueprint = route_spec.get("blueprint", None)
        is_valid, error = self._validator.validate_blueprint(blueprint)

        if not is_valid:
            raise error

        self._app.register_blueprint(blueprint)
        return True

    def add_route(self, route_spec) -> bool:
        rule = route_spec.get("rule", None)
        endpoint = route_spec.get("endpoint", None)
        methods = route_spec.get("methods", [])
        func = route_spec.get("func", None)

        valid_rule, rule_error = self._validator.validate_rule(rule)
        valid_endpoint, endpoint_error = self._validator.validate_endpoint(endpoint)
        valid_methods, methods_error = self._validator.validate_methods(methods)
        valid_func, func_error = self._validator.validate_func(func)

        is_valid = all([valid_rule, valid_endpoint, valid_methods, valid_func])

        if not is_valid:
            if rule_error:
                raise rule_error
            elif endpoint_error:
                raise endpoint_error
            elif methods_error:
                raise methods_error
            else:
                raise func_error
        
        self._app.add_url_rule(rule=rule, endpoint=endpoint, methods=methods, view_func=func)
        return True

    def handle_route(self, route_spec):
        is_blueprint = route_spec.get("is_blueprint", False)

        if is_blueprint:
            return self.add_blueprint(route_spec)
        else:
            return self.add_route(route_spec)
    
    def register_routes(self, routes_list):
        if not routes_list or not len(routes_list):
            raise ValueError("no routes given to register.")

        is_complete = all([self.handle_route(route_spec) for route_spec in routes_list])

        if is_complete:
            print("Routes and Blueprints attached successfully...")