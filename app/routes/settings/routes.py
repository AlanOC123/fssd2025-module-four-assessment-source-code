from flask import render_template, redirect, url_for, current_app, flash
from . import settings_bp
from flask_login import current_user, login_required
from .forms import UpdateProfileForm, UpdateEmailForm, UpdatePasswordForm, UpdateIdentitiesForm, UpdateThemeForm, DeleteAccountForm
from app.helper.classes.database.ProfileManager import ProfileManager
from app.helper.classes.database.DatabaseManager import DatabaseManager
from app.helper.classes.core.SessionManager import SessionManager
from app.helper.classes.core.AuthManager import AuthManager

@settings_bp.get(rule="/", endpoint="index")
@login_required
def index():
    return render_template('pages/settings/index.html', user=current_user)

@settings_bp.route(rule="/account", endpoint="account", methods=["GET", "POST"])
@login_required
def account():
    email_form = UpdateEmailForm(obj=current_user, prefix="email")
    update_password_form = UpdatePasswordForm(prefix="update-password")
    delete_account_form = DeleteAccountForm(prefix="delete")
    profile_manager: ProfileManager = current_app.db_manager.profile
    change_password_open = False
    account_deletion_open = False

    if email_form.submit_email_change.data and email_form.validate_on_submit():
        profile_data = {
            "email": email_form.email.data,
        }

        update_res = profile_manager.update_profile(current_user, **profile_data)

        if not update_res.get("success"):
            print(update_res.get("msg", ""))
            flash("Failed to update email...")

        else:
            flash(update_res.get("msg", ""), category="success")
            return redirect(url_for('settings.index'))

    elif update_password_form.submit_password_change.data and update_password_form.validate_on_submit():
        new_password_attempt = update_password_form.new_password.data
        update_res = profile_manager.change_password(current_user, new_password_attempt)

        if not update_res.get("success"):
            print(update_res.get("msg", ""))
            flash("Failed to update password...")

        else:
            flash(update_res.get("msg", ""), category="success")
            return redirect(url_for('settings.index'))
    
    elif update_password_form.submit_password_change.data:
        change_password_open = True

    elif delete_account_form.submit_deletion_request.data and delete_account_form.validate_on_submit():
        session_manager: SessionManager = current_app.session_manager
        auth_manager: AuthManager = current_app.auth_manager
        profile = current_user

        delete_res = profile_manager.delete_account(profile)

        if not delete_res.get("success"):
            print(delete_res.get("msg", ""))
            flash("Failed to delete account...")

        else:
            session_manager.clear_session()
            auth_manager.logout()
            return redirect(url_for('auth.login'))


    elif delete_account_form.submit_deletion_request.data:
        account_deletion_open = True

    return render_template(
        'pages/settings/account.html', 
        user=current_user, 
        email_form=email_form, 
        update_password_form=update_password_form,
        delete_account_form=delete_account_form, 
        change_password_open=change_password_open, 
        account_deletion_open=account_deletion_open
    )

@settings_bp.route(rule="/personal", endpoint="personal", methods=["GET", "POST"])
@login_required
def personal():
    form = UpdateProfileForm(obj=current_user)

    if form.validate_on_submit():
        profile_manager: ProfileManager = current_app.db_manager.profile

        profile_data = {
            "first_name": form.first_name.data,
            "surname": form.surname.data,
            "date_of_birth": form.date_of_birth.data,
        }

        update_res = profile_manager.update_profile(current_user, **profile_data)

        if not update_res.get("success"):
            print(update_res.get("msg", ""))
            flash("Failed to update settings...")

        else:
            flash(update_res.get("msg", ""), category="success")
            return redirect(url_for('settings.index'))


    return render_template('pages/settings/personal.html', user=current_user, form=form)

@settings_bp.route(rule="/preferences/theme", endpoint="theme", methods=["GET", "POST"])
@login_required
def theme():
    theme_form = UpdateThemeForm()
    return render_template('pages/settings/preferences.html', user=current_user, theme_form=theme_form)

@settings_bp.route(rule="/preferences/identities", endpoint="identities", methods=["GET", "POST"])
@login_required
def identities():
    identities_form = UpdateIdentitiesForm()
    return render_template('pages/settings/preferences.html', user=current_user, identities_form=identities_form)