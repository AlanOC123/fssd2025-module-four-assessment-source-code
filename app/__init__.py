from flask import Flask
from .config import config, DEFAULT
from flask_sqlalchemy import SQLAlchemy
from .routes.validation import BaseValidator
from .routes import ROUTES
from .routes.registration import RouteRegistrar

# Initialise global DB
db = SQLAlchemy()

def create_app(config_key: str):
    # Load configuration
    config_settings = config.get(config_key, DEFAULT)
    app = Flask(__name__)
    app.config.from_object(config_settings)

    # Connect DB to application instance
    db.init_app(app)

    @app.context_processor
    def inject_meta_data() -> dict:
        return dict(
            SITE_NAME = app.config.get("SITE_NAME"),
            SITE_TAGLINE = app.config.get("SITE_TAGLINE")
        )
    route_reg = RouteRegistrar(app, BaseValidator())
    route_reg.register_routes(ROUTES)

    return app