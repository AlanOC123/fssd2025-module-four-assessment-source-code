"""
Defines the API routes for managing projects.

This file contains endpoints for asynchronous operations (POST requests)
to delete and edit projects. These routes are called by JavaScript
fetch() requests from the frontend, typically from the 'Projects' page.
"""

from flask import current_app, request, jsonify, url_for
from flask_login import current_user, login_required
from . import api_bp
from app.helper.classes.database.DatabaseManager import DatabaseManager
from app.helper.classes.database.ProjectManager import ProjectManager

@api_bp.post(rule='/project/delete', endpoint='delete_project')
@login_required
def delete_project():
    """
    API endpoint to delete a project.

    This route is called via an asynchronous POST request.

    Expects:
        A JSON payload: {'projectId': <project_id>}

    On Success:
        - Deletes the project (and all its tasks via cascade).
        - Returns a 200 OK with a success message.
    
    On Failure:
        - Returns a 204 No Content if the project isn't found.
        - Returns a 500 Internal Server Error for other exceptions.
    """
    db_manager: DatabaseManager = current_app.db_manager
    project_manager: ProjectManager = db_manager.project
    try:
        # Get the JSON data from the request
        data = request.get_json()
        project_id = int(data.get("projectId"))
        
        # Call the manager to delete the project
        res = project_manager.delete_project(project_id)

        if not res.get("success", False):
            # Project not found or other deletion error
            return jsonify({ 
            "message": f"Error deleting project. Error: {res.get("msg", "")}",
            "success": False,
        }), 204 # 204 No Content is often used when a resource isn't found

        # Deletion was successful
        return jsonify({ 
            "message": f"Project deleted...",
            "success": True,
        }), 200

    except Exception as e:
        # Catch-all for server errors (e.g., failed to parse 'projectId' to int)
        return jsonify({ 
            "message": f"Error deleting project. Error: {e}",
            "success": False,
        }), 500

@api_bp.post(rule='/project/edit', endpoint='edit_project')
@login_required
def edit_project():
    """
    API endpoint to edit an existing project.

    This route is called via an asynchronous POST request.

    Expects:
        A JSON payload: {
            'projectId': <project_id>,
            'projectName': <name>,
            'projectDescription': <description>,
            'projectStartDate': <start_date_str>,
            'projectEndDate': <end_date_str>
        }

    On Success:
        - Validates and updates the project in the database.
        - Returns a 200 OK with a success message.
    
    On Failure:
        - Returns a 204 No Content if validation fails (e.g., bad dates).
        - Returns a 500 Internal Server Error for other exceptions.
    """
    db_manager: DatabaseManager = current_app.db_manager
    project_manager: ProjectManager = db_manager.project

    try:
        # --- 1. Get data from the JSON payload ---
        data = request.get_json()
        project_id = int(data.get("projectId"))
        project_name = str(data.get("projectName"))
        project_description = str(data.get("projectDescription"))
        project_start_date = str(data.get("projectStartDate"))
        project_end_date = str(data.get("projectEndDate"))

        # --- 2. Package data for the manager ---
        project_data = {
            "name": project_name,
            "description": project_description,
            "start_date": project_start_date,
            "end_date": project_end_date
        }

        # --- 3. Call the manager to edit the project ---
        res = project_manager.edit_project(project_id=project_id, **project_data)

        if not res.get("success", False):
            # Manager-level validation failed (e.g., bad name, end date before start date)
            return jsonify({ 
            "message": f"Error editing project. Error: {res.get("msg", "")}",
            "success": False,
        }), 204 # Using 204 as it's a validation/logic error, not a server crash

        # Edit was successful
        return jsonify({ 
            "message": f"Project edited...",
            "success": True,
        }), 200

    except Exception as e:
        # Catch-all for server errors (e.g., failed to parse 'projectId' to int)
        return jsonify({ 
            "message": f"Error editing project. Error: {e}",
            "success": False,
        }), 500