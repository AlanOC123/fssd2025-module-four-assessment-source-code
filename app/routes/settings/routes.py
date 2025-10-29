from flask import render_template, redirect, url_for, current_app, flash, abort
from . import settings_bp
from flask_login import current_user, login_required
from .forms import UpdateProfileForm, UpdateEmailForm, UpdatePasswordForm, UpdateIdentitiesForm, UpdateThemeColorSchemeForm, DeleteAccountForm, UpdateThemeModeForm
from app.helper.classes.database.ProfileManager import ProfileManager
from app.helper.classes.database.DatabaseManager import DatabaseManager
from app.helper.classes.database.ThemeManager import ThemeManager
from app.helper.classes.database.ProfileIdentityManager import ProfileIdentityManager
from app.helper.classes.core.SessionManager import SessionManager
from app.helper.classes.core.AuthManager import AuthManager
from app.database.models import Theme, ThemeMode
from typing import List

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
        account_deletion_open=account_deletion_open,
        pg_name="account_settings"
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


    return render_template('pages/settings/personal.html', user=current_user, form=form, pg_name="personal_settings")

@settings_bp.route(rule="/appearance", endpoint="appearance", methods=["GET", "POST"])
@login_required
def appearance():
    # Get the interface
    db_manager: DatabaseManager = current_app.db_manager
    theme_manager: ThemeManager = db_manager.theme
    profile_manager: ProfileManager = db_manager.profile

    # Get the themes
    db_res: dict = theme_manager.get_all()

    # Handle errors
    if not db_res.get("success", False):
        return abort(500)

    all_themes: List[Theme] = db_res.get("payload", {}).get("themes")
    all_modes = [(e.value, e.name.title()) for e in ThemeMode]
    all_icons = ["light_mode", "dark_mode", "computer"]

    theme_choices: list = [(t.id, t.name) for t in all_themes]

    # Build the form
    theme_scheme_form = UpdateThemeColorSchemeForm(theme_choices=theme_choices, obj=current_user)
    theme_mode_form = UpdateThemeModeForm(theme_modes=all_modes, obj=current_user)

    if theme_mode_form.submit_mode.data and theme_mode_form.validate_on_submit():
        selected_mode = theme_mode_form.theme_mode.data

        update_res = profile_manager.update_profile(current_user, theme_mode=selected_mode)

        if not update_res.get("success"):
            flash("Error setting theme mode...")
        
        else:
            flash(f"Theme Mode Set to {current_user.theme_mode.name.title()}", category="success")
    
    if theme_scheme_form.submit_scheme.data and theme_scheme_form.validate_on_submit():
        selected_theme_id = theme_scheme_form.theme_id.data
        update_res = profile_manager.update_profile(current_user, theme_id=selected_theme_id)

        if not update_res.get("success"):
            flash("Error setting color scheme...")

        else:
            flash(f"Color Scheme Set to {current_user.theme.name}", category="success")

    return render_template(
        'pages/settings/appearance.html', 
        user=current_user, 
        theme_scheme_form=theme_scheme_form, 
        theme_mode_form=theme_mode_form, 
        all_themes=all_themes, 
        theme_modes=all_modes, 
        icons=all_icons,
        pg_name="appearance_settings"
    )

@settings_bp.route(rule="/identities", endpoint="identities", methods=["GET", "POST"])
@login_required
def identities():
    # Get the user identities
    user_identities = current_user.identities
    db_manager: DatabaseManager = current_app.db_manager
    identity_manager: ProfileIdentityManager = db_manager.profile_identity

    # Init the form
    form = UpdateIdentitiesForm(identities=[
        { "id": identity.id, "name": identity.custom_name } for identity in user_identities
    ])

    # Validate the form
    if form.validate_on_submit():

        # Update the identity names
        update_res = identity_manager.update_custom_names(
            profile_id=current_user.id,
            form_data=form.identities.data
        )

        if not update_res.get("success"):
            flash(message="Error setting identity names...", category="error")
        
        else:
            count = update_res.get("payload", {}).get("updated_count", 0)
            msg = f"{count} identities updates successfully" if count != 1 else f"{count} identity updated successfully"
            flash(message=msg)

    return render_template('pages/settings/identities.html', user=current_user, form=form,         pg_name="identities_settings")