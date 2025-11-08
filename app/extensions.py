"""
Initializes and configures all Flask extensions for the application.

This file follows the 'separating extensions from app' pattern.
Extensions are instantiated here as global objects (e.g., 'db', 'csrf').
The 'init_app(app)' method is then called on these objects within
the application factory (create_app) in 'app/__init__.py'.

This prevents circular import issues, as the app-bound extensions
are not imported directly by other modules.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager

# --- 1. Database ---
# The SQLAlchemy object. This is the main ORM (Object Relational Mapper)
# that connects Flask to the PostgreSQL database.
db = SQLAlchemy()

# --- 2. Security ---
# The CSRFProtect object from Flask-WTF. This provides
# Cross-Site Request Forgery (CSRF) protection for all POST forms.
csrf = CSRFProtect()

# --- 3. User Session Management ---
# The LoginManager from Flask-Login. This handles all user session
# logic, such as logging in, logging out, and remembering users.
login_manager = LoginManager()

# --- 4. Flask-Login Configuration ---

# 'login_manager.login_view' tells Flask-Login which route (endpoint)
# to redirect unauthorized users to. If a user who is not logged in
# tries to access a @login_required page, they will be sent to 'auth.login'.
login_manager.login_view = 'auth.login'

# 'login_manager.login_message' is the flash message that will be
# shown to the user after they are redirected to the login page.
login_manager.login_message = "Log In"

# 'login_manager.login_message_category' is the 'category' of the
# flash message (e.g., 'info', 'success', 'error').
login_manager.login_message_category = "info"