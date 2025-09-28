from flask import Blueprint
from ...route_schemas import blueprint_schema

bp = Blueprint("projects", __name__, url_prefix="/project")

project_bp = blueprint_schema(bp)