from flask import current_app, request, jsonify, url_for
from flask_login import current_user, login_required
from . import api_bp
from app.helper.classes.database.DatabaseManager import DatabaseManager
from app.helper.classes.database.ThoughtManager import ThoughtManager

@api_bp.post(rule='/thought/delete', endpoint='delete_thought')
@login_required
def delete_thought():
    db_manager: DatabaseManager = current_app.db_manager
    thought_manager: ThoughtManager = db_manager.thought
    try:
        data = request.get_json()
        thought_id = int(data.get("thoughtId"))
        res = thought_manager.delete_thought(thought_id)

        if not res.get("success", False):
            return jsonify({ 
            "message": f"Error deleting thought. Error: {res.get("msg", "")}",
            "success": False,
        }), 204

        return jsonify({ 
            "message": f"Thought deleted...",
            "success": True,
        }), 200

    except Exception as e:
        return jsonify({ 
            "message": f"Error deleting thought. Error: {e}",
            "success": False,
        }), 500

@api_bp.post(rule='/thought/edit', endpoint='edit_thought')
@login_required
def edit_thought():
    db_manager: DatabaseManager = current_app.db_manager
    thought_manager: ThoughtManager = db_manager.thought

    try:
        data = request.get_json()
        thought_id = int(data.get("thoughtId"))
        content = str(data.get("content"))
        res = thought_manager.edit_thought(thought_id, content)

        if not res.get("success", False):
            return jsonify({ 
            "message": f"Error editing thought. Error: {res.get("msg", "")}",
            "success": False,
        }), 204

        return jsonify({ 
            "message": f"Thought edited...",
            "success": True,
        }), 200

    except Exception as e:
        return jsonify({ 
            "message": f"Error editing thought. Error: {e}",
            "success": False,
        }), 500