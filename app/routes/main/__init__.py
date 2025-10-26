from flask import Blueprint
from ..route_schemas import blueprint_schema

app_bp = Blueprint("app", __name__, url_prefix="/")

app_bp_schema = blueprint_schema(blueprint=app_bp)

from .routes import home, projects, tasks, thoughts