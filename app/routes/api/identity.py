"""
Defines the API routes for managing user identities.

This file contains endpoints for asynchronous operations related to
ProfileIdentities, such as setting the active identity. These routes
are typically called by JavaScript fetch() requests from the frontend.
"""

from flask import current_app, request, jsonify, url_for
from app.helper.classes.database.DatabaseManager import DatabaseManager
from app.helper.classes.database.ProfileIdentityManager import ProfileIdentityManager
from app.helper.classes.database.ProfileManager import ProfileManager
from app.helper.classes.core.SessionManager import SessionManager
from flask_login import current_user
from . import api_bp

@api_bp.post(rule="/get-identity", endpoint="get_identity")
def get_identity():
    """
    (Not Implemented) API endpoint to get the current active identity.
    
    Returns:
        json: A JSON response with a 501 Not Implemented status.
    """
    return jsonify({}), 501

# TODO Set New Identity
@api_bp.post(rule="/set-identity", endpoint="set_identity")
def set_identity():
    """
    API endpoint to set a new active identity for the current user.

    This route is called via an asynchronous POST request (e.g., fetch)
    from the frontend, typically from the 'Thoughts' page identity selector.

    Expects:
        A JSON payload: {'selectedID': <identity_id>}

    On Success:
        - Swaps the active identity in the database.
        - Updates the 'identity_id' in the Flask session.
        - Returns a JSON payload with the new identity's name and image path.
    
    On Failure:
        - Returns a JSON response with an error message and status code
          (e.g., 400 for bad request, 500 for server error).
    """
    if request.is_json:
        try:
            data = request.get_json()
            identity_id = data.get('selectedID')
            
            # Get required managers
            identity_manager: ProfileIdentityManager = current_app.db_manager.profile_identity
            session_manager: SessionManager = current_app.session_manager

            # Find the requested identity from the user's *own* list of identities
            # This is more secure than querying all identities by ID.
            selected_identity_list = [
                identity for identity in current_user.identities if identity.id == identity_id
            ]
            
            if not selected_identity_list:
                return jsonify({ "message": f"Identity not found or does not belong to user" }), 404
            
            selected_identity = selected_identity_list[0]

            # --- Get the *currently* active identity ---
            active_identity_res = identity_manager.get_active_identity(current_user)
            is_success = active_identity_res.get("success")

            if not is_success:
                # This is a fallback case, e.g., if no identity was active.
                # Just set the new one directly.
                identity_manager.set_identity(current_user, selected_identity)
                session_manager.set_identity(selected_identity.id)
                
                identity_name = selected_identity.custom_name if selected_identity.custom_name else selected_identity.template.name
                identity_image = url_for('static', filename=f"assets/avatars/{selected_identity.template.image}")
                
                # BUG FIX: Changed success to True
                return jsonify({
                    "success": True, 
                    "message": f"Identity set (no previous active identity found)", 
                    "payload": { 
                        "identityName": identity_name,
                        "identityImagePath": identity_image
                    }
                }), 200

            # --- Normal case: Swap the active identity ---
            active_identity = active_identity_res.get("payload", {}).get("active_identity")

            # Perform the swap
            swap_res = identity_manager.swap_active_identites(current_user, active_identity, selected_identity)
            is_success = swap_res.get("success", False)

            if not is_success:
                return jsonify({ "message": swap_res.get("msg", "") }), 500

            # Update the session with the new active ID
            session_manager.set_identity(selected_identity.id)

            # --- Prepare and return the success response ---
            identity_name = selected_identity.custom_name if selected_identity.custom_name else selected_identity.template.name
            identity_image = url_for('static', filename=f"assets/avatars/{selected_identity.template.image}")

            return jsonify({
                "success": True, 
                "message": f"Identity swapped successfully", 
                "payload": { 
                    "identityName": identity_name,
                    "identityImagePath": identity_image
                }
            }), 200
        
        except IndexError:
            # This happens if the list comprehension returns an empty list
            # and we try to access [0].
            return jsonify({"success": False, "message": f"Selected identity not found."}), 404
        except Exception as e:
            return jsonify({"success": False, "message": f"Error processing data: {str(e)}"}), 500
    else:
        # Request was not JSON
        return jsonify({"success": False, "message": f"Request must be JSON"}), 400

# TODO Change Identity Name
@api_bp.post(rule="/edit-identity", endpoint="edit_identity")
def edit_identity():
    """
    (Not Implemented) API endpoint to edit an identity's custom name.
    
    Returns:
        json: A JSON response with a 501 Not Implemented status.
    """
    return jsonify({}), 501