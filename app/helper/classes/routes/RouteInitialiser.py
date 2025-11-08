"""
Defines the RouteInitialiser class.

This class is the core component of the application's custom routing
system. It is instantiated by the app factory (create_app) and is
responsible for programmatically registering all routes and blueprints
with the Flask application.

It consumes the 'ROUTES' list (from app/routes/__init__.py) and uses
the 'RouteValidator' to ensure all routes are valid before registration.
"""

from .RouteValidator import RouteValidator
from flask import Flask

class RouteInitialiser():
    """
    Handles the programmatic registration of all routes and blueprints.
    
    This class is instantiated once during app creation. It validates and
    registers a list of route "schemas" (dictionaries) provided to its
    main 'register_routes' method.
    """
    _validator: RouteValidator | None = None
    _app: Flask | None = None

    def __init__(self, app: Flask, validator: RouteValidator) -> None:
        """
        Initializes the RouteInitialiser.

        Args:
            app (Flask): The Flask application instance.
            validator (RouteValidator): An instance of the RouteValidator
                                        to validate routes before registration.
        
        Raises:
            TypeError: If 'app' or 'validator' is not provided.
        """
        if validator is None:
            raise TypeError(f"Validator not provided. Add a validator to ensure routes are correctly validated {validator=}")
        
        if app is None:
            raise TypeError(f"App not provided. App required to attach routes to. {app=}")

        self._app = app
        self._validator = validator

    def _add_blueprint(self, route_spec) -> bool:
        """
        Private helper to validate and register a single Blueprint.

        Args:
            route_spec (dict): A route schema dictionary where 'is_blueprint' is True.

        Raises:
            Exception: An error from the RouteValidator if the blueprint is invalid
                       or a duplicate.

        Returns:
            bool: True on successful registration.
        """
        blueprint = route_spec.get("blueprint", None)
        
        # Use the validator to check the blueprint and for duplicates
        is_valid, error = self._validator.validate_blueprint(blueprint)

        if not is_valid:
            # Raise the specific error (e.g., TypeError, ValueError)
            raise error

        self._app.register_blueprint(blueprint)
        return True

    def _add_route(self, route_spec) -> bool:
        """
        Private helper to validate and register a single core route.

        Args:
            route_spec (dict): A route schema dictionary where 'is_blueprint' is False.

        Raises:
            Exception: An error from the RouteValidator if any part of the route
                       (rule, endpoint, methods, func) is invalid or a duplicate.

        Returns:
            bool: True on successful registration.
        """
        # Extract all route components from the schema
        rule = route_spec.get("rule", None)
        endpoint = route_spec.get("endpoint", None)
        methods = route_spec.get("methods", [])
        func = route_spec.get("func", None)

        # Validate each component using the RouteValidator
        valid_rule, rule_error = self._validator.validate_rule(rule)
        valid_endpoint, endpoint_error = self._validator.validate_endpoint(endpoint)
        valid_methods, methods_error = self._validator.validate_methods(methods)
        valid_func, func_error = self._validator.validate_func(func)

        is_valid = all([valid_rule, valid_endpoint, valid_methods, valid_func])

        # If any validation failed, raise the *first* error encountered
        if not is_valid:
            if rule_error:
                raise rule_error
            elif endpoint_error:
                raise endpoint_error
            elif methods_error:
                raise methods_error
            else:
                raise func_error
        
        # All parts are valid, register the route with Flask
        self._app.add_url_rule(rule=rule, endpoint=endpoint, methods=methods, view_func=func)
        return True

    def handle_route(self, route_spec):
        """
        Dispatcher method to route a schema to the correct helper.

        It reads the 'is_blueprint' flag from the route schema and
        calls either '_add_blueprint' or '_add_route'.

        Args:
            route_spec (dict): The route schema dictionary.

        Returns:
            bool: The result of the called helper (True on success).
        """
        is_blueprint = route_spec.get("is_blueprint", False)

        if is_blueprint:
            return self._add_blueprint(route_spec)
        else:
            return self._add_route(route_spec)
    
    def register_routes(self, routes_list):
        """
        The main public entry point for registering all routes.

        This method is called by the app factory (create_app). It
        iterates over the master list of route schemas and calls
        'handle_route' for each one.

        Args:
            routes_list (list[dict]): The master list of all route/blueprint
                                      schemas for the application (from
                                      app/routes/__init__.py).
        
        Raises:
            ValueError: If the routes_list is empty.
        """
        if not routes_list or not len(routes_list):
            raise ValueError("no routes given to register.")

        # Iterate over the entire list, calling handle_route for each.
        # all() will stop and return False if any handle_route fails.
        is_complete = all([self.handle_route(route_spec) for route_spec in routes_list])

        if is_complete:
            # Log success to the console on startup
            print("Routes and Blueprints attached successfully...")