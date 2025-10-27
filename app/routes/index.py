from .route_schemas import core_schema
from flask_login import login_required, current_user
from flask import redirect, url_for, current_app, abort
from app.helper.classes.core.SessionManager import SessionManager
from app.helper.classes.database.DatabaseManager import DatabaseManager
from app.helper.classes.database.ProfileIdentityManager import ProfileIdentityManager
from app.database.models import Profile, ProfileIdentity

def init_identity(profile: Profile):
    active_identity = False
    if not profile:
        return active_identity
    
    db: DatabaseManager = current_app.db_manager
    db_interface: ProfileIdentityManager = db.profile_identity
    session_mngr: SessionManager = current_app.session_manager

    db_res: dict = db_interface.get_active_identity(profile)

    if not db_res.get("success", False):
        db_res = db_interface.set_default_identity(profile)
        if not db_res.get("success", False):
            return False
    
    active_identity: ProfileIdentity = db_res.get("payload", {}).get("active_identity")
    session_mngr.set_identity(active_identity.id)
    return True

@login_required
def index():
    init = init_identity(profile=current_user)

    if not init:
        return abort(500)

    return redirect(url_for('app.home'))

index_route_schema = core_schema(rule="/", endpoint="index", view_func=index, methods=["GET"])