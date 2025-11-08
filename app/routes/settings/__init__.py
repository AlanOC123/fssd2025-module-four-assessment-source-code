"""
Initializes the 'settings' blueprint for the application.

This file creates the Flask Blueprint for all user settings-related
routes (e.g., /settings/account, /settings/personal).

It also imports the 'routes.py' file at the bottom to ensure that all
view functions decorated with '@settings_bp.route' are discovered and
registered with the blueprint, which helps avoid circular dependencies.
"""

from flask import Blueprint
from ..route_schemas import blueprint_schema

# Create the blueprint for all settings endpoints, prefixed with /settings
settings_bp = Blueprint("settings", __name__, url_prefix="/settings")

# Create the schema dictionary for the app's custom route initializer
settings_bp_schema = blueprint_schema(blueprint=settings_bp)

# --- Bind routes to the blueprint ---
# This import is placed at the bottom (and after 'settings_bp' is defined)
# to prevent circular import errors. The 'routes.py' file will
# import 'settings_bp' to use in its route decorators.
from .routes import account, personal, appearance, identities