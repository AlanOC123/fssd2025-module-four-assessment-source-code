from flask import jsonify, request, current_app
from app.helper.classes.database.TaskManager import TaskManager
from app.helper.classes.database.DatabaseManager import DatabaseManager
from app.helper.classes.database.ProjectManager import ProjectManager
from flask_login import login_required, current_user
from . import api_bp

@api_bp.post(rule="/tasks/status", endpoint="task_status")
@login_required
def mark_task_complete():
    db_manager: DatabaseManager = current_app.db_manager
    task_manager: TaskManager = db_manager.task

    payload = request.get_json();
    task_id = payload.get("taskId")
    
    if not task_id:
        return jsonify({
            "message": "Task ID not given...",
            "success": False
        }), 204

    task_id = int(task_id)

    print(task_id)

    db_res = task_manager.update_task_status(task_id=task_id)

    if not db_res.get("success"):
        return jsonify({
            "message": db_res.get("msg", ""),
            "success": False
        }), 500

    print(db_res)

    return jsonify({
        "message": db_res.get("msg", ""),
        "success": True
    }), 200

@api_bp.post(rule="/tasks/delete", endpoint="delete_task")
@login_required
def delete_task():
    db_manager: DatabaseManager = current_app.db_manager
    task_manager: TaskManager = db_manager.task

    payload = request.get_json();
    task_id = payload.get("taskId")
    
    if not task_id:
        return jsonify({
            "message": "Task ID not given...",
            "success": False
        }), 204
    
    db_res = task_manager.delete_task(task_id)

    if not db_res.get("success"):
        return jsonify({
            "message": db_res.get("msg", ""),
            "success": False
        }), 500

    task_id = int(task_id)

    return jsonify({
        "success": True,
        "message": db_res.get("message")
    }), 200

@api_bp.post(rule="/tasks/edit", endpoint="edit_task")
@login_required
def edit_task():
    db_manager: DatabaseManager = current_app.db_manager
    task_manager: TaskManager = db_manager.task

    payload = request.get_json();
    task_id = payload.get("taskId")
    task_name = payload.get("taskName", "")
    task_due_date = payload.get("taskDueDate", "")

    raw_data = {
        "name": task_name,
        "due_date": task_due_date
    }

    task_id = int(task_id)

    db_res = task_manager.edit_task(task_id, **raw_data)

    print(db_res)

    if not db_res.get("success"):
        return jsonify({
            "message": db_res.get("msg", ""),
            "success": False
        }), 500

    return jsonify({
        "success": True,
        "message": db_res.get("message")
    }), 200