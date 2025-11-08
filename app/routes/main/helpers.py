"""
Provides helper functions for the main 'app' blueprint.

This file contains utility functions that are called by the main
application routes (e.g., in routes.py) to perform common,
reusable tasks, such as managing the active identity in the session
or formatting dates.
"""

from app.database.models import Profile, ProfileIdentity
from app.helper.classes.database.DatabaseManager import DatabaseManager
from app.helper.classes.database.ProfileIdentityManager import ProfileIdentityManager
from app.helper.classes.core.SessionManager import SessionManager
from app.database.models import Profile, ProfileIdentity
from flask import current_app

def get_identities(profile: Profile):
    """
    DEPRECATED - This function appears to be unused in the main routes.
    
    (This helper was likely superseded by the logic inside the routes
    themselves, such as in 'projects()' or 'tasks()').

    Gets the user's active identity, setting a default if one isn't found.
    It also updates the Flask session with the active identity's ID.

    Args:
        profile (Profile): The 'current_user' Profile object.

    Returns:
        dict: A dictionary containing the 'active' ProfileIdentity object
              and a list of 'all' identities for the user. Returns an
              empty dict or None on failure.
    """
    active_identity: bool = None
    if not profile:
        return active_identity
    
    # Get all required managers from the application context
    db: DatabaseManager = current_app.db_manager
    db_interface: ProfileIdentityManager = db.profile_identity
    session_mngr: SessionManager = current_app.session_manager

    # --- 1. Try to get the currently active identity ---
    db_res: dict = db_interface.get_active_identity(profile)

    if not db_res.get("success", False):
        # --- 2. If none is active, set the default one ---
        db_res = db_interface.set_default_identity(profile)
        if not db_res.get("success", False):
            # Failed to get or set an identity, return empty dict
            return {}
    
    # --- 3. Store the active identity in the session ---
    active_identity: ProfileIdentity = db_res.get("payload", {}).get("active_identity")
    session_mngr.set_identity(active_identity.id)
    
    # --- 4. Return the data ---
    return { "active": active_identity, "all": profile.identities }

def get_ordinal_suffix(day: int) -> str:
    """
    Returns the correct English ordinal suffix (st, nd, rd, th) for a given day.

    This is used in the 'Thoughts' page to format dates like "1st", "2nd", "23rd".

    Args:
        day (int): The day of the month (e.g., 1, 21, 31).

    Returns:
        str: The corresponding ordinal suffix ("st", "nd", "rd", or "th").
    """
    # Special case for 11th, 12th, 13th, which all end in 'th'
    if 11 <= day <= 13:
        return 'th'
    
    # Use modulo 10 to get the last digit
    last_digit = day % 10
    if last_digit == 1:
        return 'st'
    elif last_digit == 2:
        return 'nd'
    elif last_digit == 3:
        return 'rd'
    else:
        # All other numbers end in 'th'
        return 'th'