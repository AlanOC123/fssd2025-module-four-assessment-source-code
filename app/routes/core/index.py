from flask import render_template, current_app, abort
from flask_login import current_user, login_required
from ..route_schemas import core_schema
from app.helper.classes.database.ProfileIdentityManager import ProfileIdentityManager

@login_required
def index():
    identity_manager: ProfileIdentityManager = current_app.db_manager.profile_identity
    identities = current_user.identities
    active_identity = [identity for identity in identities if identity.is_active]

    if not active_identity:
        default_set_res = identity_manager.set_default_identity(current_user)
        is_success = default_set_res.get("success")

        if not is_success:
            return abort(500)
        
        active_identity = default_set_res.get("payload", {}).get("active_identity")

    return render_template("pages/core/index.html", identities=identities, active_identity=active_identity[0])

main_index_route = core_schema(rule="/", endpoint="index", methods=["GET"], view_func=index)