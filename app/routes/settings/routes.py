from flask import render_template, redirect, url_for, current_app, flash
from . import settings_bp
from flask_login import current_user, login_required
from .forms import UpdateProfileForm, UpdateEmailForm, UpdatePasswordForm, UpdateIdentitiesForm, UpdateThemeForm, DeleteAccountForm
from app.helper.classes.database.ProfileManager import ProfileManager
from app.helper.classes.database.DatabaseManager import DatabaseManager

@settings_bp.get(rule="/", endpoint="index")
@login_required
def index():
    return render_template('pages/settings/index.html', user=current_user)

@settings_bp.route(rule="/account", endpoint="account", methods=["GET", "POST"])
@login_required
def account():
    email_form = UpdateEmailForm(obj=current_user)
    password_form = UpdatePasswordForm()
    delete_account_form = DeleteAccountForm()
    profile_manager: ProfileManager = current_app.db_manager.profile

    if email_form.validate_on_submit():
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

    return render_template('pages/settings/account.html', user=current_user, email_form=email_form, password_form=password_form, delete_account_form=delete_account_form)

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

@settings_bp.route(rule="/preferences", endpoint="preferences", methods=["GET", "POST"])
@login_required
def perferences():
    theme_form = UpdateThemeForm()
    identities_form = UpdateIdentitiesForm()
    return render_template('pages/settings/preferences.html', user=current_user, theme_form=theme_form, identities_form=identities_form)