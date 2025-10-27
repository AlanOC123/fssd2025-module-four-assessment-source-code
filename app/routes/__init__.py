from .index import index_route_schema
from .auth import auth_bp_schema
from .api import api_bp_schema
from .main import app_bp_schema
from .settings import settings_bp_schema

ROUTES = [
    index_route_schema,
    auth_bp_schema,
    api_bp_schema,
    app_bp_schema,
    settings_bp_schema
]