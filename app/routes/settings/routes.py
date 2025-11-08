"""
Defines the routes for the 'settings' blueprint.

This file contains the view functions for all user settings pages:
- /account: Manage email, password, and account deletion.
- /personal: Manage personal details like name and date of birth.
- /appearance: Manage color themes and light/dark mode.
- /identities: Manage custom names for user identities.

These routes handle complex form validation, including multiple
forms per page and forms dynamically populated from the database.
"""

from flask import render_template, redirect, url_for, current_app, flash, abort
from . import settings_bp
from flask_login import current_user, login_required
from .forms import (
    UpdateProfileForm, UpdateEmailForm, UpdatePasswordForm,
    UpdateIdentitiesForm, UpdateThemeColorSchemeForm, DeleteAccountForm,
    UpdateThemeModeForm
)
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
    """
    Renders the Account Settings page and handles all form submissions.
    
    This page manages three separate forms for updating email,
    updating password, and deleting the account.

    **GET Request:**
    - Renders the 'account.html' template with all three forms initialized.

    **POST Request:**
    - Checks which form was submitted (email, password, or delete).
    - Validates the submitted form.
    - On success:
        - Calls the appropriate manager (ProfileManager, AuthManager).
        - Flashes a success message.
        - Redirects to a clean URL (to prevent re-submission).
    - On validation failure:
        - Sets a flag (e.g., 'change_password_open') to True.
        - Re-renders the template. The template uses this flag
          to automatically re-open the correct form accordion
          to display the validation error.
    """
    # --- 1. Initialize all forms ---
    # Prefixes are used to distinguish the forms in the POST request
    email_form = UpdateEmailForm(obj=current_user, prefix="email")
    update_password_form = UpdatePasswordForm(prefix="update-password")
    delete_account_form = DeleteAccountForm(prefix="delete")
    
    profile_manager: ProfileManager = current_app.db_manager.profile
    
    # Flags to tell the template which accordion to re-open on error
    change_password_open = False
    account_deletion_open = False

    # --- 2. Process Email Change Form ---
    if email_form.submit_email_change.data and email_form.validate_on_submit():
        profile_data = {
            "email": email_form.email.data,
        }
        update_res = profile_manager.update_profile(current_user, **profile_data)

        if not update_res.get("success"):
            flash("Failed to update email...")
        else:
            flash(update_res.get("msg", ""), category="success")
            # Redirect to prevent form re-submission on refresh
            return redirect(url_for('settings.account')) # Changed from .index

    # --- 3. Process Password Change Form ---
    elif update_password_form.submit_password_change.data and update_password_form.validate_on_submit():
        new_password_attempt = update_password_form.new_password.data
        update_res = profile_manager.change_password(current_user, new_password_attempt)

        if not update_res.get("success"):
            flash("Failed to update password...")
        else:
            flash(update_res.get("msg", ""), category="success")
            return redirect(url_for('settings.account')) # Changed from .index
    
    elif update_password_form.submit_password_change.data:
        # Form was submitted but *failed* validation.
        # Set flag to true so the template re-opens this form.
        change_password_open = True

    # --- 4. Process Account Deletion Form ---
    elif delete_account_form.submit_deletion_request.data and delete_account_form.validate_on_submit():
        session_manager: SessionManager = current_app.session_manager
        auth_manager: AuthManager = current_app.auth_manager
        profile = current_user

        delete_res = profile_manager.delete_account(profile)

        if not delete_res.get("success"):
            flash("Failed to delete account...")
        else:
            # Account is deleted, so log the user out and clear session
            session_manager.clear_session()
            auth_manager.logout()
            return redirect(url_for('auth.login'))

    elif delete_account_form.submit_deletion_request.data:
        # Form was submitted but *failed* validation.
        # Set flag to true so the template re-opens this form.
        account_deletion_open = True

    # --- 5. Handle GET request or failed POST validation ---
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
    """
    Renders the Personal Settings page and handles profile updates.

    **GET Request:**
    - Renders 'personal.html' with the UpdateProfileForm, pre-filled
      with the current user's data.

    **POST Request:**
    - Validates the form.
    - On success:
        - Calls ProfileManager.update_profile with the new data.
        - Flashes a success message and redirects.
    - On failure:
        - Flashes an error message.
        - Re-renders the template with validation errors.
    """
    # Initialize form, pre-populating with 'current_user' data using 'obj='
    form = UpdateProfileForm(obj=current_user)

    if form.validate_on_submit():
        profile_manager: ProfileManager = current_app.db_manager.profile

        # Collect data from the form
        profile_data = {
            "first_name": form.first_name.data,
            "surname": form.surname.data,
            "date_of_birth": form.date_of_birth.data,
        }

        # Call the generic update method
        update_res = profile_manager.update_profile(current_user, **profile_data)

        if not update_res.get("success"):
            flash("Failed to update settings...")
        else:
            flash(update_res.get("msg", ""), category="success")
            return redirect(url_for('settings.personal')) # Changed from .index

    # Handle GET request or failed POST validation
    return render_template(
        'pages/settings/personal.html', 
        user=current_user, 
        form=form, 
        pg_name="personal_settings"
    )

@settings_bp.route(rule="/appearance", endpoint="appearance", methods=["GET", "POST"])
@login_required
def appearance():
    """
    Renders the Appearance Settings page and handles theme/mode changes.

    This page manages two separate forms for theme mode and color scheme.

    **GET Request:**
    - Fetches all available themes from the database.
    - Initializes the theme/mode forms, setting the 'default'
      choice based on the current user's settings.
    - Renders the 'appearance.html' template.

    **POST Request:**
    - Checks which form was submitted (mode or scheme).
    - Validates the form.
    - On success:
        - Calls ProfileManager.update_profile with the new theme/mode.
        - Flashes a success message.
    - Re-renders the template (no redirect is needed here as the
      change is immediately visible).
    """
    # --- 1. Get managers and data ---
    db_manager: DatabaseManager = current_app.db_manager
    theme_manager: ThemeManager = db_manager.theme
    profile_manager: ProfileManager = db_manager.profile

    db_res: dict = theme_manager.get_all()
    if not db_res.get("success", False):
        abort(500) # Fail hard if themes can't be loaded

    # --- 2. Prepare data for forms ---
    all_themes: List[Theme] = db_res.get("payload", {}).get("themes")
    # Data for the ThemeMode (light/dark/system) form
    all_modes = [(e.value, e.name.title()) for e in ThemeMode]
    all_icons = ["light_mode", "dark_mode", "computer"]
    # Data for the ThemeColorScheme (e.g., "Ocean Blue") form
    theme_choices: list = [(t.id, t.name) for t in all_themes]

    # --- 3. Initialize forms ---
    # 'obj=current_user' pre-selects the user's current choice
    theme_scheme_form = UpdateThemeColorSchemeForm(theme_choices=theme_choices, obj=current_user)
    theme_mode_form = UpdateThemeModeForm(theme_modes=all_modes, obj=current_user)

    # --- 4. Process Theme Mode Form ---
    if theme_mode_form.submit_mode.data and theme_mode_form.validate_on_submit():
        selected_mode = theme_mode_form.theme_mode.data
        update_res = profile_manager.update_profile(current_user, theme_mode=selected_mode)

        if not update_res.get("success"):
            flash("Error setting theme mode...")
        else:
            flash(f"Theme Mode Set to {current_user.theme_mode.name.title()}", category="success")
    
    # --- 5. Process Theme Scheme Form ---
    if theme_scheme_form.submit_scheme.data and theme_scheme_form.validate_on_submit():
        selected_theme_id = theme_scheme_form.theme_id.data
        update_res = profile_manager.update_profile(current_user, theme_id=selected_theme_id)

        if not update_res.get("success"):
            flash("Error setting color scheme...")
        else:
            flash(f"Color Scheme Set to {current_user.theme.name}", category="success")

    # --- 6. Handle GET request or render after POST ---
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
    """
    Renders the Identities Settings page and handles custom name updates.
    
    This page uses a WTForms FieldList to render a form for every
    identity the user has.

    **GET Request:**
    - Fetches all of the user's ProfileIdentity objects.
    - Pre-populates the FieldList form with data for each identity.
    - Renders the 'identities.html' template.

    **POST Request:**
    - Validates the FieldList form (checking all fields).
    - On success:
        - Calls the IdentityManager to bulk-update all names.
        - Flashes a success message with the count of updated items.
    - On failure:
        - Flashes an error message.
    - Re-renders the template with any validation errors.
    """
    # --- 1. Get data and managers ---
    user_identities = current_user.identities
    db_manager: DatabaseManager = current_app.db_manager
    identity_manager: ProfileIdentityManager = db_manager.profile_identity
    updated_ids = [] # Used to show the "saved" checkmark in the template

    # --- 2. Initialize the FieldList Form ---
    # We must pre-populate the form with the user's existing data.
    # This list comprehension builds the 'data' structure WTForms expects.
    form_data = [{ 
            "identity_id": identity.id, 
            "identity_custom_name": identity.custom_name if identity.custom_name else identity.template.name 
        } 
        for identity in user_identities
    ]
    form = UpdateIdentitiesForm(identities=form_data)

    # --- 3. Process POST Request ---
    if form.validate_on_submit():
        # The form is valid, call the manager to update the names.
        # The manager is smart and only updates names that have changed.
        update_res = identity_manager.update_custom_names(
            profile_id=current_user.id,
            form_data=form.identities.data
        )

        if not update_res.get("success"):
            flash(message="Error setting identity names...", category="error")
        else:
            # Get the list of IDs that were *actually* updated
            updated_ids = update_res.get("payload", {}).get("updated", [])
            count = len(updated_ids)
            msg = f"{count} identities updated successfully" if count != 1 else f"{count} identity updated successfully"
            flash(message=msg, category="success")

    # --- 4. Handle GET request or render after POST ---
    return render_template(
        'pages/settings/identities.html', 
        user=current_user, 
        identities=user_identities, # Pass the original objects for the template
        form=form,                 # Pass the form for rendering
        pg_name="identities_settings",
        updated_ids=updated_ids    # Pass the list of updated IDs
    )