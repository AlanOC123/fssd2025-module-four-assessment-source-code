"""
Initializes the main 'app' blueprint for the application.

This file creates the Flask Blueprint for all core application routes
(e.g., /app/home, /app/projects), which are intended for
logged-in users.

It also imports the 'routes.py' file at the bottom to ensure that all
view functions decorated with '@app_bp.route' are discovered and
registered with the blueprint, which helps avoid circular dependencies.
"""

from flask import Blueprint
from ..route_schemas import blueprint_schema

# Create the blueprint for all main application endpoints, prefixed with /app
app_bp = Blueprint("app", __name__, url_prefix="/app")

# Create the schema dictionary for the app's custom route initializer
app_bp_schema = blueprint_schema(blueprint=app_bp)

# --- Bind routes to the blueprint ---
# This import is placed at the bottom (and after 'app_bp' is defined)
# to prevent circular import errors. The 'routes.py' file will
# import 'app_bp' to use in its decorators.
from .routes import home, projects, tasks, thoughts