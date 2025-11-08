"""
Defines the configuration classes for the Flask application.

This file loads environment variables from a .env file and defines
separate configuration classes (Default, Production, Testing)
to manage different environments. The 'create_app' factory in
app/__init__.py uses this file to load the correct settings.
"""

import os
from dotenv import load_dotenv
from datetime import timedelta

# Load environment variables from a .env file (e.g., SECRET_KEY)
# This makes them available in os.environ
load_dotenv()

class DefaultConfig():
    """
    Base configuration class.

    Contains default settings that are shared across all environments
    or provide a fallback if an environment variable is not set.
    """
    # 1. Security
    # SECRET_KEY is used by Flask for session signing and CSRF protection.
    # It's loaded from the .env file or defaults to an insecure key for development.
    SECRET_KEY = os.environ.get("SECRET_KEY") or "unsecure_dev_key"

    # 2. SQLAlchemy
    # Disables a Flask-SQLAlchemy feature that tracks object modifications
    # and emits signals, which adds unnecessary overhead.
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 3. Custom Application Metadata
    # These are custom settings used by the app's templates and managers.
    SITE_NAME = "Projectify"
    SITE_TAGLINE = "Organise Thoughts into Actions"
    
    # Password complexity rules (used by PasswordManager and forms)
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_MAX_LENGTH = 128
    PASSWORD_CONTAINS_SYMBOL = True
    PASSWORD_CONTAINS_CAP = True
    
    # Flask-Login "Remember Me" cookie duration
    REMEMBER_COOKIE_DURATION = timedelta(days=30)

class ProductionConfig(DefaultConfig):
    """
    Configuration for the production (live) environment.

    Inherits from DefaultConfig and overrides settings for deployment
    (e.g., on Render).
    """
    # 1. Database
    # Loads the production database URL from the 'DATABASE_URL_PROD' env var.
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL_PROD")

    # 2. App State
    # Ensures Flask and extensions run in production-optimized mode
    # (e.g., debug=False).
    TESTING = False

class TestingConfig(DefaultConfig):
    """
    Configuration for the local development and testing environment.

    Inherits from DefaultConfig and overrides settings for development.
    """
    # 1. Database
    # Loads the testing/development database URL from the 'DATABASE_URL_TEST' env var.
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL_TEST")

    # 2. App State
    # Enables Flask's testing/debug mode.
    TESTING = True

    # 3. Test User Data
    # Defines a test user dictionary used by the 'flask seed-db' command
    # *only* when TESTING=True.
    TEST_USER = {
        "first_name": "Alan",
        "surname": "O'Connor",
        "date_of_birth": "1995-11-07",
        "email": "testuser@projectify.com",
        "password": "Test!12345",
        "theme_name": "Default"
    }

# A dictionary mapping config keys to their respective classes.
# This is used by the 'create_app' factory to select the environment
# based on the FLASK_CONFIG environment variable.
config = {
    "default": DefaultConfig,
    "production": ProductionConfig,
    "testing": TestingConfig
}

# A fallback alias for the DefaultConfig.
DEFAULT = DefaultConfig