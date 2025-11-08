"""
Manages all database operations for the Project model.

This file defines the ProjectManager class, which is responsible for
the business logic of creating, editing, deleting, and querying projects.
It also includes logic for managing a project's status based on its tasks
and handling the 'active' project for a given identity.
"""

from .BaseManager import BaseManager
from .ProfileIdentityManager import ProfileIdentityManager
from app.database.models import Project, Status
from app.helper.functions.response_schemas import success_res, error_res
from datetime import date, timedelta, datetime
from sqlalchemy import select

class ProjectManager(BaseManager):
    """
    Handles all CRUD and business logic operations for Projects.
    
    Inherits from BaseManager to get access to the session, cache,
    and generic helper methods.
    """
    def __init__(self, db_manager_instance) -> None:
        """
        Initializes the ProjectManager.

        Args:
            db_manager_instance (DatabaseManager): The central DB manager.
        """
        super().__init__(db_manager_instance)

    def get_project_by_id(self, project_id):
        """
        Retrieves a single project by its primary key.

        This is a simple, direct getter that bypasses the standardized
        response system for internal use by other managers.

        Args:
            project_id (int): The primary key of the project to retrieve.

        Returns:
            Project | None: The SQLAlchemy Project object if found, else None.
        """
        if not project_id:
            return None
        
        # .get() is the most efficient way to query by primary key
        return self._session.get(Project, project_id)
    
    def create_project(self, **project_data):
        """
        Validates and creates a new project in the database.

        Args:
            **project_data: Keyword arguments containing project details
                            (name, description, identity_id, owner_id,
                            start_date, end_date, status).

        Returns:
            dict: A standardized success or error response dictionary.
        """
        # --- 1. Get the data ---
        name = project_data.get("name", "")
        description = project_data.get("description", "")
        identity_id = project_data.get("identity_id", None)
        owner_id = project_data.get("owner_id", None)
        start_date = project_data.get("start_date", date.today())
        end_date = project_data.get("end_date", timedelta(days=30) + date.today())
        status = project_data.get("status", Status.NOT_STARTED.value)

        # --- 2. Clean the data ---
        name = name.strip()
        description = description.strip()
        # Ensure status is the enum's value (e.g., 'not_started')
        if isinstance(status, Status):
            status = status.value

        # --- 3. Validate the data ---
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

        # Validate that the end date is not before the start date
        timedifference = end_date - start_date
        number_of_days = timedifference.days
        if number_of_days < 0:
            return error_res(f"End date less than start date...")

        # --- 4. Add to session and commit ---
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
        """
        Deletes a project from the database.
        
        Associated tasks are deleted automatically via the 'cascade'
        option set on the Project model's relationship.

        Args:
            project_id (int): The ID of the project to delete.

        Returns:
            dict: A standardized success or error response dictionary.
        """
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
        """
        Validates and updates an existing project in the database.

        This method only updates fields that are explicitly provided
        in the **project_data argument and are not empty strings.

        Args:
            project_id (int): The ID of the project to edit.
            **project_data: Keyword arguments for the fields to update
                            (e.g., name, description, start_date, end_date).

        Returns:
            dict: A standardized success or error response dictionary.
        """
        if not project_id:
            return error_res("Project ID not given...")
        
        project = self.get_project_by_id(project_id=project_id)

        if not project:
            return error_res("Project not found...")

        # A dictionary to hold only the validated data that needs to be updated.
        data_to_update = {}

        # Store the dates as they are. They will be updated if new
        # date data is passed in. This is for the final validation step.
        start_date = project.start_date
        end_date = project.end_date
        
        try:
            # --- 1. Validate and collect data ---
            for key, value in project_data.items():
                # Skip any empty or None values
                if value is None or value is "":
                    continue

                if key == "name":
                    name = str(value).strip()
                    if name == project.name: # Skip if no change
                        continue
                    if not 5 <= len(name) <= 100:
                        return error_res("Invalid project name. Must be between 5 and 100 characters")
                    data_to_update["name"] = name
                
                elif key == "description":
                    description = str(value).strip()
                    if description == project.description: # Skip if no change
                        continue
                    data_to_update["description"] = value

                elif key == "start_date":
                    # Convert string from form/API into a date object
                    start_date = datetime.strptime(str(value), '%Y-%m-%d').date()
                    data_to_update["start_date"] = start_date

                elif key == "end_date":
                    # Convert string from form/API into a date object
                    end_date = datetime.strptime(str(value), '%Y-%m-%d').date()
                    data_to_update["end_date"] = end_date
        
        except ValueError as e:
            # Catches the datetime.strptime() error
            return error_res(f"Invalid data provided: {e}")
        except Exception as e:
            return error_res(f"An unexpected error occurred: {e}")
        
        # --- 2. Final validation ---
        if end_date < start_date:
            return error_res("End date is before start date...")
        
        if not data_to_update:
            return error_res("No valid data to update...")
        
        # --- 3. Apply updates ---
        # Loop through the validated data and set attributes on the model
        for key, value in data_to_update.items():
            if hasattr(project, key):
                setattr(project, key, value)
        
        # --- 4. Commit changes ---
        try:
            self._session.add(project)
            self._session.commit()
            return success_res(msg="Project updated!", payload={})
        except Exception as e:
            self._session.rollback()
            return error_res(f"Error updating project. Error {e}")
        
    def get_projects_by_status(self, profile_id, identity_id, status_key):
        """
        Gets all projects for a specific user and identity, with an
        optional filter by status.

        Args:
            profile_id (int): The user's profile ID.
            identity_id (int): The profile identity's ID.
            status_key (str | None): A string key ('not_started', 'in_progress',
                                     'completed', 'all', or None).

        Returns:
            dict: A standardized success or error response dictionary.
        """
        if not profile_id:
            return error_res("Profile not given...")

        if not identity_id:
            return error_res("Identity not given...")
        
        # Build the base query:
        # SELECT * FROM projects WHERE owner_id = ? AND identity_id = ?
        query = select(Project).where(
            Project.owner_id == profile_id,
            Project.identity_id == identity_id
        )

        # Check for a status key and add it to the query
        if status_key and status_key != "all":
            status_map = {
                "not_started": Status.NOT_STARTED.value,
                "in_progress": Status.IN_PROGRESS.value,
                "completed": Status.COMPLETED.value,
            }
            # If its a valid key, add the WHERE clause
            if status_key in status_map:
                query = query.where(Project.status == status_map.get(status_key))
        
        try:
            # Get all projects matching the query
            projects = self._session.scalars(query).all()
            return success_res(msg="Projects found!", payload={ "projects": projects })

        except Exception as e:
            return error_res(f"Error getting projects. Error {e}")
    
    def update_project_status(self, project_id) -> dict:
        """
        Recalculates and updates a project's status based on its tasks.

        This method is designed to be called *within* another transaction
        (like when a task is created or updated). It adds the change to the
        session but does NOT commit it. The calling function is responsible
        for the final commit or rollback.

        Args:
            project_id (int): The ID of the project to update.

        Returns:
            dict: A standardized success or error response.
        """
        if not project_id:
            return error_res("Project not given...")
        
        project = self._session.get(Project, project_id)
        if not project:
            return error_res("Project not found...")

        tasks = project.tasks
        total_task_count = len(tasks)

        # --- This is the core business logic for project status ---
        if total_task_count == 0:
            # No tasks = Not Started
            project.status = Status.NOT_STARTED.value
        elif all(task.is_complete for task in tasks):
            # All tasks complete = Completed
            project.status = Status.COMPLETED.value
        else:
            # Any other state (some tasks complete, none complete) = In Progress
            project.status = Status.IN_PROGRESS.value
        
        try:
            # Stage the change to the session.
            self._session.add(project)
            return success_res(msg="Project status updated!", payload={})
        except Exception as e:
            # We don't rollback here, as we're part of a larger transaction.
            return error_res(f"Error updating project status. Error: {e}")
    
    def deactivate_projects(self, identity):
        """
        Sets 'is_active' to False for all projects in a given identity.
        
        This is a helper method for 'set_active_project' to ensure
        only one project can be active at a time.

        Args:
            identity (ProfileIdentity): The identity object.

        Returns:
            dict: A standardized success or error response dictionary.
        """
        if not identity:
            return error_res("Identity not given...")

        projects = identity.projects
        if not projects:
            # No projects to deactivate, so this is a success.
            return success_res(msg="Projects deactivated!", payload={})
        
        # Set all projects to inactive and stage them for commit
        for project in projects:
            project.is_active = False
            self._session.add(project)
        
        try:
            # This method *does* commit, as it's a self-contained action.
            self._session.commit()
            return success_res(msg="Projects deactivated!", payload={})
        except Exception as e:
            self._session.rollback()
            return error_res(f"Error updating project status. Error: {e}")
    
    def set_default_project(self, identity):
        """
        Finds and sets a default active project if none is set.
        
        The "default" is the project with the least time remaining.

        Args:
            identity (ProfileIdentity): The identity object.

        Returns:
            dict: A standardized success or error response dictionary.
        """
        if not identity:
            return error_res("Identity not given...")
        
        projects = identity.projects
        if not projects:
            return error_res("No projects found...")
        
        # Sort projects by the 'time_left' property (defined in models.py)
        sorted_projects = sorted(
            projects,
            key=lambda project: project.time_left
        )
        # The first project in the sorted list is the default
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
        """
        Gets the currently active project for a given identity.
        
        If no project is active, it calls 'set_default_project' to
        designate one.

        Args:
            identity (ProfileIdentity): The identity object.

        Returns:
            dict: A standardized success or error response dictionary.
        """
        if not identity:
            return error_res("Identity not given...")

        projects = identity.projects
        if not projects:
            # It's not an error to have no projects.
            return success_res(msg="No projects found!", payload={ "active_project": None })
        
        # Find the project that has is_active == True
        active_project_list = list(filter(
            lambda project: project.is_active,
            projects
        ))

        if not active_project_list:
            # No project was active, so we must set one.
            default_project_res = self.set_default_project(identity=identity)

            if not default_project_res.get("success"):
                return error_res("Failed to get active project...")

            active_project = default_project_res.get("payload", {}).get("active_project")
        
        else:
            # An active project was found.
            active_project = active_project_list[0]
        
        return success_res(msg="Project found!", payload={"active_project": active_project})
    
    def set_active_project(self, identity, project_id):
        """
        Sets a specific project as active.

        This performs two actions in a transaction:
        1. Calls 'deactivate_projects' to set all projects to inactive.
        2. Sets the specified 'project_id' as active.

        Args:
            identity (ProfileIdentity): The identity object.
            project_id (int): The ID of the project to set as active.

        Returns:
            dict: A standardized success or error response dictionary.
        """
        if not project_id:
            return error_res("Project not given...")
        
        # --- 1. Deactivate all other projects ---
        deactivated_res = self.deactivate_projects(identity=identity)
        if not deactivated_res.get("success"):
            return error_res("Error setting active project....")
        
        # --- 2. Activate the new project ---
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

