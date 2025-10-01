from flask import Flask
from .config import config, DEFAULT
from flask_sqlalchemy import SQLAlchemy
from .helper.classes.routes.RouteInitialiser import RouteInitialiser
from .helper.classes.routes.RouteValidator import RouteValidator
from .helper.classes.core.SessionManager import SessionManager

def get_db():
    from flask import current_app

    if 'sqlalchemy' not in current_app.extensions:
        raise RuntimeError("SQLAlchemy extension not initialised on the app")
    return current_app.extensions["sqlalchemy"]

# Initialise global DB
db = SQLAlchemy()
db_manager = None
session_manager = SessionManager()

def create_app(config_key: str):
    # DB Manager accessible globally
    global db_manager

    # Load configuration
    config_settings = config.get(config_key, DEFAULT)
    app = Flask(__name__)
    app.config.from_object(config_settings)

    # Connect DB to application instance and set up manager
    db.init_app(app)
    from .helper.classes.database.DatabaseManager import DatabaseManager

    db_manager = DatabaseManager(app)

    @app.context_processor
    def inject_meta_data() -> dict:
        return dict(
            SITE_NAME = app.config.get("SITE_NAME"),
            SITE_TAGLINE = app.config.get("SITE_TAGLINE")
        )

    # Attach routes
    from .routes import ROUTES
    route_reg = RouteInitialiser(app, RouteValidator())
    route_reg.register_routes(ROUTES)

    return app