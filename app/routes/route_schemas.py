"""
Defines standardized schema functions for registering routes.

This file provides helper functions that create consistent dictionary
structs for a single route ('core_schema') or a Blueprint
('blueprint_schema').

These schemas are used by the 'RouteInitialiser' class to
programmatically register all routes and blueprints with the
Flask application during initialization.
"""

def blueprint_schema(blueprint) -> dict:
    """
    Creates a standardized dictionary schema for a Blueprint.

    Args:
        blueprint (Blueprint): The Flask Blueprint object to be registered.

    Returns:
        dict: A dictionary schema recognized by the RouteInitialiser.
    """
    return {
        "is_blueprint": True,
        "blueprint": blueprint
    }

def core_schema(rule, endpoint, view_func, methods) -> dict:
    """
    Creates a standardized dictionary schema for a single, non-blueprint route.

    Args:
        rule (str): The URL rule for the route (e.g., "/").
        endpoint (str): The unique endpoint name for 'url_for()' (e.g., "index").
        view_func (function): The view function that handles this route.
        methods (list[str]): A list of HTTP methods this route accepts
                             (e.g., ["GET", "POST"]).

    Returns:
        dict: A dictionary schema recognized by the RouteInitialiser.
    """
    return {
        "is_blueprint": False,
        "rule": rule,
        "endpoint": endpoint,
        "func": view_func,
        "methods": methods
    }