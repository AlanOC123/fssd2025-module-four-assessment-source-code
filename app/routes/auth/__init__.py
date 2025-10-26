from flask import Blueprint
from ..route_schemas import blueprint_schema

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

auth_bp_schema = blueprint_schema(blueprint=auth_bp)

from .routes import login, register, logout