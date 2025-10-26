from app.routes.route_schemas import blueprint_schema
from flask import Blueprint

# Create the blueprint
api_bp = Blueprint("api", __name__, url_prefix="/api")

# Create the Schema
api_bp_schema = blueprint_schema(blueprint=api_bp)

# Bind routes
from .identity import get_identity, set_identity, edit_identity