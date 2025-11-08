"""
Defines the API routes for managing tasks.

This file contains endpoints for asynchronous operations (POST requests)
to change a task's status, delete a task, and edit a task. These
routes are called by JavaScript fetch() requests from the 'Tasks' page.
"""

from flask import jsonify, request, current_app
from app.helper.classes.database.TaskManager import TaskManager
from app.helper.classes.database.DatabaseManager import DatabaseManager
from app.helper.classes.database.ProjectManager import ProjectManager
from flask_login import login_required, current_user
from . import api_bp

@api_bp.post(rule="/tasks/status", endpoint="task_status")
@login_required
def mark_task_complete():
    """
    API endpoint to toggle a task's 'is_complete' status.

    This route is called via an asynchronous POST request. It expects
    a JSON payload containing the ID of the task to update.

    Expects:
        A JSON payload: {'taskId': <task_id>}

    On Success:
        - Toggles the task's status in the database.
        - Atomically updates the parent project's status.
        - Returns a 200 OK with a success message.
    
    On Failure:
        - Returns a 204 No Content if the 'taskId' is missing.
        - Returns a 500 Internal Server Error if the database update fails.
    """
    # Get the database manager
    db_manager: DatabaseManager = current_app.db_manager
    task_manager: TaskManager = db_manager.task

    # Get the JSON payload from the request
    payload = request.get_json();
    task_id = payload.get("taskId")
    
    if not task_id:
        # No ID was provided
        return jsonify({
            "message": "Task ID not given...",
            "success": False
        }), 204

    # The TaskManager handles the atomic transaction
    db_res = task_manager.update_task_status(task_id=int(task_id))

    if not db_res.get("success"):
        # The transaction failed (e.g., task not found, project update failed)
        return jsonify({
            "message": db_res.get("msg", ""),
            "success": False
        }), 500

    # The transaction succeeded
    return jsonify({
        "message": db_res.get("msg", ""),
        "success": True
    }), 200

@api_bp.post(rule="/tasks/delete", endpoint="delete_task")
@login_required
def delete_task():
    """
    API endpoint to delete a task.

    This route is called via an asynchronous POST request.

    Expects:
        A JSON payload: {'taskId': <task_id>}

    On Success:
        - Deletes the task.
        - Atomically updates the parent project's status.
        - Returns a 200 OK with a success message.
    
    On Failure:
        - Returns a 204 No Content if the 'taskId' is missing.
        - Returns a 500 Internal Server Error if the database update fails.
    """
    db_manager: DatabaseManager = current_app.db_manager
    task_manager: TaskManager = db_manager.task

    payload = request.get_json();
    task_id = payload.get("taskId")
    
    if not task_id:
        return jsonify({
            "message": "Task ID not given...",
            "success": False
        }), 204
    
    # The TaskManager handles the atomic deletion and project update
    db_res = task_manager.delete_task(int(task_id))

    if not db_res.get("success"):
        return jsonify({
            "message": db_res.get("msg", ""),
            "success": False
        }), 500

    return jsonify({
        "success": True,
        "message": db_res.get("msg", "Task deleted successfully")
    }), 200

@api_bp.post(rule="/tasks/edit", endpoint="edit_task")
@login_required
def edit_task():
    """
    API endpoint to edit an existing task's details.

    This route is called via an asynchronous POST request.

    Expects:
        A JSON payload: {
            'taskId': <task_id>,
            'taskName': <name>,
            'taskDueDate': <date_str>
        }

    On Success:
        - Validates and updates the task in the database.
        - Returns a 200 OK with a success message.
    
    On Failure:
        - Returns a 500 Internal Server Error if validation or DB update fails.
    """
    db_manager: DatabaseManager = current_app.db_manager
    task_manager: TaskManager = db_manager.task

    # --- 1. Get data from the JSON payload ---
    payload = request.get_json();
    task_id = payload.get("taskId")
    task_name = payload.get("taskName", "")
    task_due_date = payload.get("taskDueDate", "")

    # --- 2. Package data for the manager ---
    raw_data = {
        "name": task_name,
        "due_date": task_due_date
    }

    # --- 3. Call the manager to edit the task ---
    db_res = task_manager.edit_task(int(task_id), **raw_data)

    if not db_res.get("success"):
        # Manager-level validation failed (e.g., bad name, invalid date)
        return jsonify({
            "message": db_res.get("msg", ""),
            "success": False
        }), 500 # 500 indicates a server-side validation/DB failure

    # Edit was successful
    return jsonify({
        "success": True,
        "message": db_res.get("msg", "Task updated successfully")
    }), 200