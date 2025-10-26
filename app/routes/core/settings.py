from flask import render_template, url_for, redirect, request, current_app, abort
from flask_login import current_user, login_required
from app.helper.classes.database.ProfileIdentityManager import ProfileIdentityManager
from ..route_schemas import core_schema
from .forms.settings import EditProfile, EditIdentities, EditTheme

@login_required
def settings():
    identities = current_user.identities
    identity_manager:ProfileIdentityManager = current_app.db_manager.profile_identity

    active_identity_res = identity_manager.get_active_identity(current_user)
    is_success = active_identity_res.get("success", False)

    if not is_success:
        return abort(500)
    
    active_identity = active_identity_res.get("payload", {}).get("active_identity")

    return render_template('pages/core/settings.html', identities=identities, active_identity=active_identity)

settings_route = core_schema(rule="/settings", endpoint="settings", methods=["GET"], view_func=settings)