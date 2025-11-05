from .BaseManager import BaseManager
from .ProfileIdentityManager import ProfileIdentityManager
from app.database.models import Project, Status
from app.helper.functions.response_schemas import success_res, error_res
from datetime import date, timedelta, datetime
from sqlalchemy import select

class ProjectManager(BaseManager):
    def __init__(self, db_manager_instance) -> None:
        super().__init__(db_manager_instance)

    def get_project_by_id(self, project_id):
        if not project_id:
            return None
        
        return self._session.get(Project, project_id)
    
    def create_project(self, **project_data):
        # Get the data
        name = project_data.get("name", "")
        description = project_data.get("description", "")
        identity_id = project_data.get("identity_id", None)
        owner_id = project_data.get("owner_id", None)
        start_date = project_data.get("start_date", date.today())
        end_date = project_data.get("end_date", timedelta(days=30) + date.today())
        status = project_data.get("status", Status.NOT_STARTED.value)

        # Clean the data
        name = name.strip()
        description = description.strip()
        status = status.value

        # Validate the data
        if not identity_id:
            return error_res("Orphaned project detected. Not attached to Identity...")

        if not owner_id:
            return error_res("Orphaned project detected. Not attached to Profile...")
        
        if not name:
            return error_res("Invalid project name...")
        
        if not (5 < len(name) < 100):
            return error_res("Project name must be between 5 and 100 characters long...")
        
        if len(description) > 500:
            return error_res(f"Description too long. Must be less than 500 characters...")

        timedifference = end_date - start_date

        number_of_days = timedifference.days

        if number_of_days < 0:
            return error_res(f"End date less than start date...")

        # Add to session
        try:
            project = Project(
                name=name,
                description=description,
                owner_id=owner_id,
                identity_id=identity_id,
                start_date=start_date,
                end_date=end_date,
                status=status
            )
            self._session.add(project)
            self._session.commit()
            return success_res(msg="New Project created!", payload={})

        except Exception as e:
            self._session.rollback()
            return error_res(f"Error creating project. Error {e}")

    def delete_project(self, project_id):
        if not project_id:
            return error_res("Project ID not given...")
        
        project = self.get_project_by_id(project_id=project_id)

        if not project:
            return error_res("Project not found...")
        
        try:
            self._session.delete(project)
            self._session.commit()
            return success_res(msg="Project deleted...", payload={})
        except Exception as e:
            self._session.rollback()
            return error_res(f"Error deleting project. Error: {e}")

    def edit_project(self, project_id, **project_data):
        if not project_id:
            return error_res("Project ID not given...")
        
        project = self.get_project_by_id(project_id=project_id)

        if not project:
            return error_res("Project not found...")

        data_to_update = {}

        start_date = project.start_date
        end_date = project.end_date
        
        try:
            for key, value in project_data.items():
                if value is None or value is "":
                    continue

                if key == "name":
                    name = str(value).strip()

                    if name == project.name:
                        continue

                    if not 5 <= len(name) <= 100:
                        return error_res("Invalid project name. Must be between 5 and 100 characters")
                    
                    data_to_update["name"] = name
                
                elif key == "description":
                    description = str(value).strip()

                    if description == project.description:
                        continue

                    data_to_update["description"] = value

                elif key == "start_date":
                    start_date = datetime.strptime(str(value), '%Y-%m-%d').date()
                    data_to_update["start_date"] = start_date

                elif key == "end_date":
                    end_date = datetime.strptime(str(value), '%Y-%m-%d').date()
                    data_to_update["end_date"] = end_date
        except ValueError as e:
            return error_res(f"Invalid data provided: {e}")
        except Exception as e:
            return error_res(f"An unexpected error occurred: {e}")
        
        if end_date < start_date:
            return error_res("End date is before start date...")
        
        if not data_to_update:
            return error_res("No valid data to update...")
        
        for key, value in data_to_update.items():
            if hasattr(project, key):
                setattr(project, key, value)
        
        try:
            self._session.add(project)
            self._session.commit()
            return success_res(msg="Project updated!", payload={})
        except Exception as e:
            self._session.rollback()
            return error_res(f"Error updating project. Error {e}")
        
    def get_projects_by_status(self, profile_id, identity_id, status_key):
        if not profile_id:
            return error_res("Profile not given...")

        if not identity_id:
            return error_res("Identity not given...")
        
        # Build the query
        query = select(Project).where(Project.owner_id == profile_id and Project.identity_id == identity_id)

        # Check for a status key and update the query
        if status_key and status_key != "all":
            status_map = {
                "not_started": Status.NOT_STARTED.value,
                "in_progress": Status.IN_PROGRESS.value,
                "completed": Status.COMPLETED.value,
            }

            # If its a valid key update the query
            if status_key in status_map:
                query = query.where(Project.status == status_map.get(status_key))
        
        try:
            # Get the projects from the DB
            projects = self._session.scalars(query).all()
            return success_res(msg="Projects found!", payload={ "projects": projects })

        except Exception as e:
            return error_res(f"Error getting projects. Error {e}")
    
    def update_project_status(self, project_id) -> dict:
        if not project_id:
            return error_res("Project not given...")
        
        # Get the project
        project = self._session.get(Project, project_id)

        if not project:
            return error_res("Project not found...")

        tasks = project.tasks
        total_task_count = len(tasks)

        if total_task_count == 0:
            project.status = Status.NOT_STARTED.value
        
        elif all(task.is_complete for task in tasks):
            project.status = Status.COMPLETED.value
        
        else:
            project.status = Status.IN_PROGRESS.value
        
        try:
            self._session.add(project)
            return success_res(msg="Project status updated!", payload={})
        except Exception as e:
            return error_res(f"Error updating project status. Error: {e}")
    
    def deactivate_projects(self, identity):
        if not identity:
            return error_res("Identity not given...")

        projects = identity.projects

        if not projects:
            return success_res(msg="Projects deactivated!", payload={})
        
        for project in projects:
            project.is_active = False
            self._session.add(project)
        
        try:
            self._session.commit()
            return success_res(msg="Projects deactivated!", payload={})
        except Exception as e:
            self._session.rollback()
            return error_res(f"Error updating project status. Error: {e}")
    
    def set_default_project(self, identity):
        if not identity:
            return error_res("Identity not given...")
        
        projects = identity.projects

        if not projects:
            return error_res("No projects found...")
        
        sorted_projects = sorted(
            projects,
            key=lambda project: project.time_left
        )

        default_project = sorted_projects[0]

        try:
            default_project.is_active = True
            self._session.add(default_project)
            self._session.commit()
            return success_res(msg="Default project set", payload={ "active_project": default_project })
        except Exception as e:
            self._session.rollback()
            return error_res(f"Error updating project status. Error: {e}")
    
    def get_active_project(self, identity):
        if not identity:
            return error_res("Identity not given...")

        projects = identity.projects

        if not projects:
            return success_res(msg="No projects found!", payload={ "active_project": None })
        
        active_project_list = list(filter(
            lambda project: project.is_active,
            projects
        ))

        if not active_project_list:
            default_project_res = self.set_default_project(identity=identity)

            if not default_project_res.get("success"):
                return error_res("Failed to get active project...")

            active_project = default_project_res.get("active_project")
        
        else:
            active_project = active_project_list[0]
        
        return success_res(msg="Project found!", payload={"active_project": active_project})
    
    def set_active_project(self, identity, project_id):
        if not project_id:
            return error_res("Project not given...")
        
        deactivated_res = self.deactivate_projects(identity=identity)

        if not deactivated_res.get("success"):
            return error_res("Error setting active project....")
        
        project = self._session.get(Project, project_id)

        if not project:
            return error_res("Project not found...")
        
        try:
            project.is_active = True
            self._session.add(project)
            self._session.commit()
            return success_res(msg="Default project set", payload={ "active_project": project })
        except Exception as e:
            self._session.rollback()
            return error_res(f"Error updating project status. Error: {e}")

