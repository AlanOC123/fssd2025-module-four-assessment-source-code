from app.database.models import Profile, ProfileIdentity
from app.helper.classes.database.DatabaseManager import DatabaseManager
from app.helper.classes.database.ProfileIdentityManager import ProfileIdentityManager
from app.helper.classes.core.SessionManager import SessionManager
from app.database.models import Profile, ProfileIdentity
from flask import current_app

def get_identities(profile: Profile):
    active_identity: bool = None
    if not profile:
        return active_identity
    
    db: DatabaseManager = current_app.db_manager
    db_interface: ProfileIdentityManager = db.profile_identity
    session_mngr: SessionManager = current_app.session_manager

    db_res: dict = db_interface.get_active_identity(profile)

    if not db_res.get("success", False):
        db_res = db_interface.set_default_identity(profile)
        if not db_res.get("success", False):
            return {}
    
    active_identity: ProfileIdentity = db_res.get("payload", {}).get("active_identity")
    session_mngr.set_identity(active_identity.id)
    return { "active": active_identity, "all": profile.identities }

def get_ordinal_suffix(day):
    if 11 <= day <= 13:
        return 'th'
    elif day % 10 == 1:
        return 'st'
    elif day % 10 == 2:
        return 'nd'
    elif day % 10 == 3:
        return 'rd'
    else:
        return 'th'