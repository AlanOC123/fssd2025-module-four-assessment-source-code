"""
Defines the authentication routes for the application.

This file contains the view functions for logging a user in, registering
a new user, and logging a user out. It handles form validation,
interacts with the appropriate managers (AuthManager, ProfileManager,
SessionManager), and manages user sessions and flash messages.
"""

from flask import render_template, redirect, url_for, current_app, flash
from . import auth_bp
from .forms import LoginForm, RegisterForm
from app.helper.classes.database.DatabaseManager import DatabaseManager
from app.helper.classes.database.ProfileManager import ProfileManager
from app.helper.classes.database.ProfileIdentityManager import ProfileIdentityManager
from app.helper.classes.core.SessionManager import SessionManager
from app.helper.classes.core.AuthManager import AuthManager
from app.database.models import Profile
from flask_login import current_user

@auth_bp.route(rule="/login", endpoint="login", methods=["GET", "POST"])
def login():
    """
    Renders the login page and handles the user login process.

    **GET Request:**
    - Renders the login.html template.
    - If the user is already authenticated, redirects to the main index page.
    
    **POST Request:**
    - Validates the LoginForm.
    - On success:
        1. Calls the AuthManager to verify credentials and log the user in.
        2. Sets the user's default active identity in the Flask session.
        3. Flashes a success message and redirects to the main index page.
    - On failure (invalid form or credentials):
        1. Flashes an error message.
        2. Renders the login.html template again with validation errors.
    """
    # If user is already logged in, send them to the main app
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()

    if form.validate_on_submit():
        # --- Get Required Managers ---
        auth_manager: AuthManager = current_app.auth_manager
        
        # --- 1. Attempt to log the user in ---
        auth_res: dict = auth_manager.login(
            form.email.data,
            form.password.data,
            form.remember_me.data
        )

        is_success = auth_res.get("success", False)

        if is_success:
            # --- 2. Login was successful, set up the session ---
            active_identity = None
            profile: Profile = auth_res.get("payload", {}).get("profile")
            profile_identity_manager: ProfileIdentityManager = current_app.db_manager.profile_identity
            session_manager: SessionManager = current_app.session_manager

            # Get the user's active identity, or set a default one
            profile_identity_res = profile_identity_manager.get_active_identity(profile)
            if not profile_identity_res.get("success"):
                profile_identity_res = profile_identity_manager.set_default_identity(profile)
            
            active_identity = profile_identity_res.get("payload", {}).get("active_identity")

            # Store the active identity ID in the session
            if active_identity:
                session_manager.set_identity(active_identity.id)

            # --- 3. Redirect to the app ---
            flash(message=auth_res.get("msg", ""), category="success")
            return redirect(url_for('index'))

        if not is_success:
            # Authentication failed (invalid email/password)
            flash(message=auth_res.get("msg", ""), category="error")
    
    # Render the page on GET request or if form validation failed
    return render_template('pages/auth/login.html', form=form, pg_name="Log In")

@auth_bp.route(rule="/register", endpoint="register", methods=["POST", "GET"])
def register():
    """
    Renders the registration page and handles new user creation.

    **GET Request:**
    - Renders the register.html template.
    - If the user is already authenticated, redirects to the main index page.

    **POST Request:**
    - Validates the RegisterForm (including custom password/email validators).
    - On success:
        1. Calls the ProfileManager to create the new profile.
           (This is an atomic transaction that also creates default identities).
        2. Flashes a success message.
        3. Redirects to the login page.
    - On failure (invalid form or duplicate email):
        1. Flashes an error message.
        2. Renders the register.html template again with validation errors.
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegisterForm()

    if form.validate_on_submit():
        # --- Get Required Manager ---
        profile_manager: ProfileManager = current_app.db_manager.profile

        # --- 1. Collect Form Data ---
        profile_data = {
            "first_name": form.first_name.data,
            "surname": form.surname.data,
            "date_of_birth": form.dob.data,
            "email": form.email.data,
            "password": form.password.data,
            "theme_name": "Default", # New users get the default theme
            "stay_logged_in": False
        }

        # --- 2. Attempt to Create Profile ---
        # This single call handles validation, hashing, and the
        # atomic creation of the profile and its default identities.
        profile_res: dict = profile_manager.create_profile(**profile_data)

        is_success = profile_res.get("success", False)

        if is_success:
            # --- 3. Success ---
            flash(message=profile_res.get("msg", ""), category="success")
            return redirect(url_for('auth.login'))

        if not is_success:
            # --- 4. Failure (e.g., duplicate email, validation error) ---
            flash(message=profile_res.get("msg", ""), category="error")

    # Render the page on GET request or if form validation failed
    return render_template('pages/auth/register.html', form=form)

@auth_bp.get(rule="/logout", endpoint="logout")
def logout():
    """
    Logs the user out and clears the session.
    
    - Clears all data from the Flask session (including active identity).
    - Calls Flask-Login's logout_user() function.
    - Flashes an info message.
    - Redirects to the login page.
    """
    auth_manager:AuthManager = current_app.auth_manager
    session_manager: SessionManager = current_app.session_manager

    # Clear our custom session data (e.g., active_identity_id)
    session_manager.clear_session()
    # Log the user out of Flask-Login
    auth_manager.logout()

    flash(message="Logged Out...", category="info")

    return redirect(url_for("auth.login"))