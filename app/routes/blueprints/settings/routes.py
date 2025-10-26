from flask import render_template, redirect, url_for, current_app, flash
from . import settings_bp
from flask_login import current_user, login_required

@settings_bp.get(rule="/", endpoint="nav")
@login_required
def nav():
    return render_template('pages/settings/nav.html')

@settings_bp.get(rule="/", endpoint="account")
@login_required
def account():
    return render_template('pages/settings/account.html')

@settings_bp.get(rule="/", endpoint="account")
@login_required
def personal():
    return render_template('pages/settings/personal.html')