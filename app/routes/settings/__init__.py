from flask import Blueprint
from ..route_schemas import blueprint_schema

settings_bp = Blueprint("settings", __name__, url_prefix="/settings")

settings_bp_schema = blueprint_schema(blueprint=settings_bp)

from .routes import index, account, personal 