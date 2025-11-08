"""
Central registry for all application routes and blueprints.

This file imports the route/blueprint schema dictionaries from all other
route packages (auth, api, main, info, settings) and the main index route.

It aggregates them into a single 'ROUTES' list. This list is
then imported by the main application factory (in app/__init__.py)
and used by the RouteInitialiser to register all routes and
blueprints with the Flask app instance.
"""

from .index import index_route_schema
from .auth import auth_bp_schema
from .api import api_bp_schema
from .main import app_bp_schema
from .settings import settings_bp_schema
from .info import info_bp_schema

# This list defines all routes and blueprints to be registered
# with the application. It is imported by create_app() in
# app/__init__.py and processed by the RouteInitialiser.
ROUTES = [
    index_route_schema,
    auth_bp_schema,
    api_bp_schema,
    app_bp_schema,
    settings_bp_schema, 
    info_bp_schema
]