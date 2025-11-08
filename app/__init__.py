"""
Defines the main application factory, 'create_app'.

This file is the entry point for the Flask application. It uses the
application factory pattern to create and configure a Flask app instance.
It initializes all extensions, registers blueprints and routes,
sets up the custom manager architecture, and registers CLI commands.
"""

from flask import Flask
from .config import config, DEFAULT
from .extensions import db, csrf, login_manager
from .seed.commands import register_commands
from flask_migrate import Migrate

def get_db():
    """
    A helper function to safely retrieve the SQLAlchemy extension.
    
    This is used by the BaseManager to get access to the database
    session within the application context.
    
    Raises:
        RuntimeError: If SQLAlchemy has not been initialized on the app.
        
    Returns:
        SQLAlchemy: The initialized SQLAlchemy extension object.
    """
    from flask import current_app

    if 'sqlalchemy' not in current_app.extensions:
        raise RuntimeError("SQLAlchemy extension not initialised on the app")
    return current_app.extensions["sqlalchemy"]

def create_app(config_key: str):
    """
    The application factory.
    
    This function builds and configures the Flask application instance.
    
    Args:
        config_key (str): The key for the configuration to use
                          (e.g., "production", "testing").
                          
    Returns:
        Flask: The configured Flask application instance.
    """
    # --- 1. Load configuration ---
    config_settings = config.get(config_key, DEFAULT)
    app = Flask(__name__)
    app.config.from_object(config_settings)

    # --- 2. Initialize Flask extensions ---
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    
    # --- 3. Import and attach custom managers ---
    # These imports are done here to avoid circular dependencies
    from .helper.classes.routes.RouteInitialiser import RouteInitialiser
    from .helper.classes.routes.RouteValidator import RouteValidator
    from .helper.classes.core.SessionManager import SessionManager
    from .helper.classes.core.AuthManager import AuthManager
    from .helper.classes.database.ProfileManager import ProfileManager, PasswordManager
    from .helper.classes.database.DatabaseManager import DatabaseManager

    # This is your "Service Locator" pattern.
    # We instantiate all managers and attach them directly to the 'app'
    # object, making them accessible via 'current_app.db_manager', etc.
    app.db_manager = DatabaseManager(app.config)
    app.session_manager = SessionManager()
    
    # The AuthManager needs the ProfileManager's PasswordManager
    auth_pw_manager = app.db_manager.profile.pw_manager or PasswordManager(app.config)
    app.auth_manager = AuthManager(app.db_manager.profile, auth_pw_manager)
    
    # Initialize Flask-Migrate for database migrations
    migrate = Migrate(app, db)

    # --- 4. Configure Flask-Login ---
    @login_manager.user_loader
    def load_user(profile_id: int):
        """
        Flask-Login callback to reload the user object from the session.
        
        This function is called on every request for an authenticated user.
        It uses the 'profile_id' stored in the session to fetch the
        full Profile object.
        
        Args:
            profile_id (int): The user's ID (primary key) from the session.
            
        Returns:
            Profile | None: The Profile object if found, otherwise None.
        """
        db_res = app.db_manager.profile.get_profile_by_id(profile_id)
        is_success = db_res.get("success", False)

        if not is_success:
            return None

        return db_res.get("payload", {}).get("profile")

    # --- 5. Register Context Processors ---
    @app.context_processor
    def inject_meta_data() -> dict:
        """
        Injects global variables into all Jinja2 templates.
        
        This makes variables like 'SITE_NAME' available in any
        template without having to pass them in 'render_template()'.
        
        Returns:
            dict: A dictionary of variables to inject.
        """
        return dict(
            SITE_NAME = app.config.get("SITE_NAME"),
            SITE_TAGLINE = app.config.get("SITE_TAGLINE"),
            PASSWORD_MIN_LENGTH = app.config.get("PASSWORD_MIN_LENGTH"),
            PASSWORD_MAX_LENGTH = app.config.get("PASSWORD_MAX_LENGTH")
        )

    # --- 6. Register all routes and blueprints ---
    # This uses your custom routing system
    from .routes import ROUTES
    route_reg = RouteInitialiser(app, RouteValidator())
    route_reg.register_routes(ROUTES)

    # --- 7. Register custom CLI commands ---
    # This makes 'flask seed-db' and 'flask reset-db' available
    register_commands(app)

    # --- 8. Register custom Jinja filters ---
    # Adds the built-in 'zip' function as a filter in Jinja
    app.jinja_env.filters["zip"] = zip

    return app