from flask import Blueprint
from ..route_schemas import blueprint_schema

info_bp = Blueprint('info', __name__, url_prefix="/info")

from .routes import about, sitemap

info_bp_schema = blueprint_schema(blueprint=info_bp)