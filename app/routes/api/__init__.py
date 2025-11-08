"""
Initializes the API blueprint for the application.

This file creates the Flask Blueprint for all API-related routes
(e.g., /api/...). These routes are designed to be called asynchronously
by frontend JavaScript (e.g., fetch requests).

It also imports all the endpoint files (identity.py, thoughts.py, etc.)
at the bottom to ensure their route decorators (@api_bp.route)
are executed and registered with the blueprint.
"""

from app.routes.route_schemas import blueprint_schema
from flask import Blueprint

# Create the blueprint for all API endpoints, prefixed with /api
api_bp = Blueprint("api", __name__, url_prefix="/api")

# Create the schema dictionary for the app's custom route initializer
api_bp_schema = blueprint_schema(blueprint=api_bp)

# --- Bind routes to the blueprint ---
# These imports are placed at the bottom to avoid circular dependencies.
# Simply importing them here executes the code within (i.e., the
# @api_bp.route decorators), which registers them with the 'api_bp'.
from .identity import get_identity, set_identity, edit_identity
from .thoughts import delete_thought, edit_thought
from .projects import delete_project, edit_project
from .tasks import mark_task_complete, edit_task, delete_task