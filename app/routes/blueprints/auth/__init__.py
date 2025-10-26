from flask import Blueprint
from ...route_schemas import blueprint_schema

bp = Blueprint("auth", __name__, url_prefix="/auth")

auth_bp = blueprint_schema(bp)

from .routes import login, register, logout