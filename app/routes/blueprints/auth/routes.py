from flask import render_template, redirect, url_for, current_app, flash
from . import bp
from .forms import LoginForm, RegisterForm
from app.helper.classes.database.DatabaseManager import DatabaseManager
from app.helper.classes.database.ProfileManager import ProfileManager
from app.helper.classes.database.ProfileIdentityManager import ProfileIdentityManager
from app.helper.classes.core.SessionManager import SessionManager
from app.helper.classes.core.AuthManager import AuthManager
from app.database.models import Profile
from flask_login import current_user

@bp.route(rule="/login", endpoint="login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()

    if form.validate_on_submit():
        auth_manager: AuthManager = current_app.auth_manager
        auth_res: dict = auth_manager.login(
            form.email.data,
            form.password.data,
            form.remember_me.data
        )

        is_success = auth_res.get("success", False)

        if is_success:
            active_identity = None
            profile: Profile = auth_res.get("payload", {}).get("profile")
            profile_identity_manager: ProfileIdentityManager = current_app.db_manager.profile_identity
            session_manager: SessionManager = current_app.session_manager

            profile_identity_res = profile_identity_manager.get_active_identity(profile)
            is_success = profile_identity_res.get("success")

            if not is_success:
                profile_identity_res = profile_identity_manager.set_default_identity(profile)
            
            active_identity = profile_identity_res.get("payload", {}).get("active_identity")

            print(active_identity)
            
            session_manager.set_identity(active_identity.id)

            flash(message=auth_res.get("msg", ""), category="success")
            return redirect(url_for('index'))

        if not is_success:
            flash(message=auth_res.get("msg", ""), category="error")
    
    return render_template('pages/auth/login.html', form=form, pg_name="Log In")

@bp.route(rule="/register", endpoint="register", methods=["POST", "GET"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegisterForm()

    if form.validate_on_submit():
        profile_manager: ProfileManager = current_app.db_manager.profile

        profile_data = {
            "first_name": form.first_name.data,
            "last_name": form.last_name.data,
            "date_of_birth": form.dob.data,
            "email": form.email.data,
            "password": form.password.data,
        }

        profile_res: dict = profile_manager.create_profile(**profile_data)

        is_success = profile_res.get("success", False)

        if is_success:
            flash(message=profile_res.get("msg", ""))
            return redirect(url_for('auth.login'))

        if not is_success:
            flash(message=profile_res.get("msg", ""))
    
    return render_template('pages/auth/register.html', form=form)

@bp.get(rule="/logout", endpoint="logout")
def logout():
    auth_manager:AuthManager = current_app.auth_manager
    session_manager: SessionManager = current_app.session_manager

    session_manager.clear_session()
    auth_manager.logout()

    flash(message="Logged Out...", category="info")

    return redirect(url_for("auth.login"))