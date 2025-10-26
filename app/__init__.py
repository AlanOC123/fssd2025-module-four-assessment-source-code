from flask import Flask
from .config import config, DEFAULT
from .extensions import db, csrf, login_manager
from .seed.commands import register_commands
from flask_migrate import Migrate

def get_db():
    from flask import current_app

    if 'sqlalchemy' not in current_app.extensions:
        raise RuntimeError("SQLAlchemy extension not initialised on the app")
    return current_app.extensions["sqlalchemy"]

def create_app(config_key: str):
    # Load configuration
    config_settings = config.get(config_key, DEFAULT)
    app = Flask(__name__)
    app.config.from_object(config_settings)

    # Connect DB to application instance and set up manager
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    from .helper.classes.routes.RouteInitialiser import RouteInitialiser
    from .helper.classes.routes.RouteValidator import RouteValidator
    from .helper.classes.core.SessionManager import SessionManager
    from .helper.classes.core.AuthManager import AuthManager
    from .helper.classes.database.ProfileManager import ProfileManager, PasswordManager
    from .helper.classes.database.DatabaseManager import DatabaseManager

    app.db_manager = DatabaseManager(app.config)
    app.session_manager = SessionManager()
    auth_pw_manager = app.db_manager.profile.pw_manager or PasswordManager(app.config)
    app.auth_manager = AuthManager(app.db_manager.profile, auth_pw_manager)
    migrate = Migrate(app, db)

    @login_manager.user_loader
    def load_user(profile_id: int):
        db_res = app.db_manager.profile.get_profile_by_id(profile_id)

        is_success = db_res.get("success", False)

        if not is_success:
            return None

        return db_res.get("payload", {}).get("profile")

    @app.context_processor
    def inject_meta_data() -> dict:
        return dict(
            SITE_NAME = app.config.get("SITE_NAME"),
            SITE_TAGLINE = app.config.get("SITE_TAGLINE"),
            PASSWORD_MIN_LENGTH = app.config.get("PASSWORD_MIN_LENGTH"),
            PASSWORD_MAX_LENGTH = app.config.get("PASSWORD_MAX_LENGTH")
        )

    # Attach routes
    from .routes import ROUTES
    route_reg = RouteInitialiser(app, RouteValidator())
    route_reg.register_routes(ROUTES)

    register_commands(app)

    return app