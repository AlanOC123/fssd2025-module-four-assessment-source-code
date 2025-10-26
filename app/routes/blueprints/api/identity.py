from flask import current_app, request, jsonify, url_for
from app.helper.classes.database.DatabaseManager import DatabaseManager
from app.helper.classes.database.ProfileIdentityManager import ProfileIdentityManager
from app.helper.classes.database.ProfileManager import ProfileManager
from app.helper.classes.core.SessionManager import SessionManager
from flask_login import current_user
from . import bp

# TODO Get Active Identity
@bp.post(rule="/get-identity", endpoint="get_identity")
def get_identity():
    return jsonify({}), 501

# TODO Set New Identity
@bp.post(rule="/set-identity", endpoint="set_identity")
def set_identity():
    if request.is_json:
        try:
            data = request.get_json()
            identity_id = data.get('selectedID')
            identity_manager: ProfileIdentityManager = current_app.db_manager.profile_identity
            session_manager: SessionManager = current_app.session_manager

            # Find the requested identity
            selected_identity = [
                identity for identity in current_user.identities if identity.id == identity_id
            ][0]

            # Error Handling if not found
            if not selected_identity:
                return jsonify({ "message": f"Identity not found" }), 204
            
            # Set the selected identity
            active_identity_res = identity_manager.get_active_identity(current_user)
            is_success = active_identity_res.get("success")

            if not is_success:
                identity_manager.set_identity(current_user, selected_identity)
                session_manager.set_identity(selected_identity.id)
                identity_name = selected_identity.custom_name if selected_identity.custom_name else selected_identity.template.name
                identity_image = url_for('static', filename=f"assets/avatars/{selected_identity.template.image}")
                return jsonify({
                    "success": False, 
                    "message": f"Found identity", 
                    "payload": { 
                        "identityName": identity_name,
                        "identityImagePath": identity_image
                    }
                }), 200

            active_identity = active_identity_res.get("payload", {}).get("active_identity")

            swap_res = identity_manager.swap_active_identites(current_user, active_identity, selected_identity)

            is_success = swap_res.get("success", False)

            if not is_success:
                return jsonify({ "message": swap_res.get("msg", "") }), 500

            identity_name = selected_identity.custom_name if selected_identity.custom_name else selected_identity.template.name
            identity_image = url_for('static', filename=f"assets/avatars/{selected_identity.template.image}")

            return jsonify({
                "success": False, 
                "message": f"Found identity", 
                "payload": { 
                    "identityName": identity_name,
                    "identityImagePath": identity_image
                }
            }), 200
        except Exception as e:
            return jsonify({"success": False, "message": f"Error processing data: {str(e)}"}), 500
    else:
        return jsonify({"success": False, "message": f"Request must be JSON"}), 400

# TODO Change Identity Name
@bp.post(rule="/edit-identity", endpoint="edit_identity")
def edit_identity():
    return jsonify({}), 501