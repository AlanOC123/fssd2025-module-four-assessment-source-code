"""
Initializes the Authentication blueprint for the application.

This file creates the Flask Blueprint for all authentication-related
routes (e.g., /auth/login, /auth/register).

It also imports the 'routes.py' file at the bottom to ensure that all
view functions decorated with '@auth_bp.route' are discovered and
registered with the blueprint, avoiding circular dependencies.
"""

from flask import Blueprint
from ..route_schemas import blueprint_schema

# Create the blueprint for all authentication endpoints, prefixed with /auth
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# Create the schema dictionary for the app's custom route initializer
auth_bp_schema = blueprint_schema(blueprint=auth_bp)

# --- Bind routes to the blueprint ---
# This import is placed at the bottom to avoid circular dependencies.
# Simply importing 'routes.py' executes the code within, registering
# the view functions (login, register, logout) with the 'auth_bp'.
from .routes import login, register, logout