"""
Initializes the 'info' blueprint for the application.

This file creates the Flask Blueprint for all static informational
routes (e.g., /info/about, /info/sitemap).

It also imports the 'routes.py' file at the bottom to ensure that all
view functions decorated with '@info_bp.route' are discovered and
registered with the blueprint, which helps avoid circular dependencies.
"""

from flask import Blueprint
from ..route_schemas import blueprint_schema

# Create the blueprint for all informational endpoints, prefixed with /info
info_bp = Blueprint('info', __name__, url_prefix="/info")

# --- Bind routes to the blueprint ---
# This import is placed *after* the blueprint 'info_bp' is created
# to prevent circular import errors, as 'routes.py' will
# need to import 'info_bp' to use it in its decorators.
from .routes import about, sitemap

# Create the schema dictionary for the app's custom route initializer
info_bp_schema = blueprint_schema(blueprint=info_bp)