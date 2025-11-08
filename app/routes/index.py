"""
Defines the main index route (/) for the application.

This file handles the root URL. Its primary responsibility is to ensure
a logged-in user has an active identity set in their session before
redirecting them to the main application homepage (/app/home).
"""

from .route_schemas import core_schema
from flask_login import login_required, current_user
from flask import redirect, url_for, current_app, abort
from app.helper.classes.core.SessionManager import SessionManager
from app.helper.classes.database.DatabaseManager import DatabaseManager
from app.helper.classes.database.ProfileIdentityManager import ProfileIdentityManager
from app.database.models import Profile, ProfileIdentity

def init_identity(profile: Profile) -> bool:
    """
    Ensures a user has an active identity set in their Flask session.

    This helper function checks if the user's profile already has an
    'is_active' identity.
    
    - If it does, it sets that identity's ID in the session.
    - If it does not (e.g., on first login), it calls the manager to
      set a default identity.
    - If setting a default fails, it returns False.

    Args:
        profile (Profile): The 'current_user' object.

    Returns:
        bool: True if an identity was successfully found/set and stored
              in the session. False if an error occurred.
    """
    if not profile:
        return False
    
    # --- 1. Get required managers ---
    db: DatabaseManager = current_app.db_manager
    db_interface: ProfileIdentityManager = db.profile_identity
    session_mngr: SessionManager = current_app.session_manager

    # --- 2. Try to find an already-active identity ---
    db_res: dict = db_interface.get_active_identity(profile)

    if not db_res.get("success", False):
        # --- 3. If none found, attempt to set a default ---
        db_res = db_interface.set_default_identity(profile)
        if not db_res.get("success", False):
            # This is a critical failure (e.g., user has no identities)
            return False
    
    # --- 4. Store the found/set identity in the session ---
    active_identity: ProfileIdentity = db_res.get("payload", {}).get("active_identity")
    session_mngr.set_identity(active_identity.id)
    return True

@login_required
def index():
    """
    View function for the root URL (/).

    **Route:** /
    **Method:** GET
    **Protection:** @login_required

    This route is for authenticated users only. Its sole purpose is to
    initialize the user's active identity (via `init_identity`) and
    then immediately redirect them to the main application's home page.

    Aborts with a 500 error if identity initialization fails.
    """
    # Run the helper to ensure the session has an active identity
    init = init_identity(profile=current_user)

    if not init:
        # If this fails, something is wrong with the user's account
        # (e.g., they have no identities).
        return abort(500)

    # Success. Redirect to the main app.
    return redirect(url_for('app.home'))

# The schema used by the custom route initializer in app/__init__.py
index_route_schema = core_schema(rule="/", endpoint="index", view_func=index, methods=["GET"])