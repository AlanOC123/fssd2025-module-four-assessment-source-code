from flask import current_app, request, jsonify, url_for
from flask_login import current_user, login_required
from . import api_bp
from app.helper.classes.database.DatabaseManager import DatabaseManager
from app.helper.classes.database.ProjectManager import ProjectManager

@api_bp.post(rule='/project/delete', endpoint='delete_project')
@login_required
def delete_project():
    db_manager: DatabaseManager = current_app.db_manager
    project_manager: ProjectManager = db_manager.project
    try:
        data = request.get_json()
        project_id = int(data.get("projectId"))
        res = project_manager.delete_project(project_id)

        if not res.get("success", False):
            return jsonify({ 
            "message": f"Error deleting project. Error: {res.get("msg", "")}",
            "success": False,
        }), 204

        return jsonify({ 
            "message": f"Project deleted...",
            "success": True,
        }), 200

    except Exception as e:
        return jsonify({ 
            "message": f"Error deleting project. Error: {e}",
            "success": False,
        }), 500

@api_bp.post(rule='/project/edit', endpoint='edit_project')
@login_required
def edit_project():
    db_manager: DatabaseManager = current_app.db_manager
    project_manager: ProjectManager = db_manager.project

    try:
        data = request.get_json()
        project_id = int(data.get("projectId"))
        project_name = str(data.get("projectName"))
        project_description = str(data.get("projectDescription"))
        project_start_date = str(data.get("projectStartDate"))
        project_end_date = str(data.get("projectEndDate"))

        project_data = {
            "name": project_name,
            "description": project_description,
            "start_date": project_start_date,
            "end_date": project_end_date
        }

        print(project_data)
        res = project_manager.edit_project(project_id=project_id, **project_data)

        print(res)

        if not res.get("success", False):
            return jsonify({ 
            "message": f"Error editing project. Error: {res.get("msg", "")}",
            "success": False,
        }), 204

        return jsonify({ 
            "message": f"Project edited...",
            "success": True,
        }), 200

    except Exception as e:
        return jsonify({ 
            "message": f"Error editing project. Error: {e}",
            "success": False,
        }), 500