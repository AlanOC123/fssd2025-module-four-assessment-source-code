"""
Defines the API routes for managing thoughts.

This file contains endpoints for asynchronous operations (POST requests)
to delete and edit a user's thoughts. These routes are called by
JavaScript fetch() requests from the 'Thoughts' page.
"""

from flask import current_app, request, jsonify, url_for
from flask_login import current_user, login_required
from . import api_bp
from app.helper.classes.database.DatabaseManager import DatabaseManager
from app.helper.classes.database.ThoughtManager import ThoughtManager

@api_bp.post(rule='/thought/delete', endpoint='delete_thought')
@login_required
def delete_thought():
    """
    API endpoint to delete a thought.

    This route is called via an asynchronous POST request.

    Expects:
        A JSON payload: {'thoughtId': <thought_id>}

    On Success:
        - Deletes the thought from the database.
        - Returns a 200 OK with a success message.
    
    On Failure:
        - Returns a 204 No Content if the thought isn't found.
        - Returns a 500 Internal Server Error for other exceptions.
    """
    db_manager: DatabaseManager = current_app.db_manager
    thought_manager: ThoughtManager = db_manager.thought
    try:
        # Get the JSON data from the request
        data = request.get_json()
        thought_id = int(data.get("thoughtId"))
        
        # Call the manager to delete the thought
        res = thought_manager.delete_thought(thought_id)

        if not res.get("success", False):
            # Thought not found or other deletion error
            return jsonify({ 
            "message": f"Error deleting thought. Error: {res.get("msg", "")}",
            "success": False,
        }), 204 # 204 No Content is appropriate if the resource wasn't found

        # Deletion was successful
        return jsonify({ 
            "message": f"Thought deleted...",
            "success": True,
        }), 200

    except Exception as e:
        # Catch-all for server errors (e.g., failed to parse 'thoughtId' to int)
        return jsonify({ 
            "message": f"Error deleting thought. Error: {e}",
            "success": False,
        }), 500

@api_bp.post(rule='/thought/edit', endpoint='edit_thought')
@login_required
def edit_thought():
    """
    API endpoint to edit an existing thought.

    This route is called via an asynchronous POST request.

    Expects:
        A JSON payload: {
            'thoughtId': <thought_id>,
            'content': <new_content_string>
        }

    On Success:
        - Validates and updates the thought in the database.
        - Returns a 200 OK with a success message.
    
    On Failure:
        - Returns a 204 No Content if validation fails (e.g., thought not found).
        - Returns a 500 Internal Server Error for other exceptions.
    """
    db_manager: DatabaseManager = current_app.db_manager
    thought_manager: ThoughtManager = db_manager.thought

    try:
        # --- 1. Get data from the JSON payload ---
        data = request.get_json()
        thought_id = int(data.get("thoughtId"))
        content = str(data.get("content"))
        
        # --- 2. Call the manager to edit the thought ---
        res = thought_manager.edit_thought(thought_id, content)

        if not res.get("success", False):
            # Manager-level validation failed (e.g., thought not found)
            return jsonify({ 
            "message": f"Error editing thought. Error: {res.get("msg", "")}",
            "success": False,
        }), 204

        # Edit was successful
        return jsonify({ 
            "message": f"Thought edited...",
            "success": True,
        }), 200

    except Exception as e:
        # Catch-all for server errors (e.g., failed to parse 'thoughtId' to int)
        return jsonify({ 
            "message": f"Error editing thought. Error: {e}",
            "success": False,
        }), 500