"""
Manages all database operations for the Task model.

This file defines the TaskManager class, which handles the business logic
for creating, editing, deleting, and querying tasks. It works closely
with the ProjectManager to ensure that a project's status is automatically
updated whenever one of its tasks is modified (an atomic transaction).
"""

from .BaseManager import BaseManager
from .ProjectManager import ProjectManager
from app.database.models import Task, Difficulty, Project
from app.helper.functions.response_schemas import success_res, error_res
from datetime import date, timedelta, datetime
from sqlalchemy import select

class TaskManager(BaseManager):
    """
    Handles all CRUD and business logic operations for Tasks.
    
    This class ensures that any changes to a task (creation, deletion,
    status change) are reflected in the parent project's overall status
    within a single, atomic database transaction.
    """
    def __init__(self, db_manager_instance) -> None:
        """
        Initializes the TaskManager.

        Args:
            db_manager_instance (DatabaseManager): The central DB manager.
        """
        super().__init__(db_manager_instance)

    def create_task(self, **raw_data):
        """
        Validates and creates a new task, then updates the parent project's
        status in an atomic transaction.

        Args:
            **raw_data: Keyword arguments with task details (name, project_id,
                          due_date, difficulty).

        Returns:
            dict: A standardized success or error response dictionary.
        """
        # Get the ProjectManager from the central DatabaseManager
        from .DatabaseManager import DatabaseManager
        db_manager: DatabaseManager = self._db_manager
        project_manager: ProjectManager = db_manager.project

        # --- 1. Get and validate data ---
        today: date = date.today()
        name: str = raw_data.get("name", "")
        project_id: int | None = raw_data.get("project_id", )
        due_date: date = raw_data.get("due_date", timedelta(days=30) + today)
        difficulty: Difficulty = raw_data.get("difficulty", Difficulty.MEDIUM)

        task_data: dict = {}

        if not name:
            return error_res("Task name not given...")
        
        if not 5 < len(name.strip()) < 100:
            return error_res("Invalid task name not given...")
        
        if not project_id:
            return error_res("Project id not given...")
        
        if due_date < today:
            return error_res("Task is already overdue...")
        
        # --- 2. Sanitize and prepare data ---
        task_data["name"] = str(name).strip()
        task_data["project_id"] = int(project_id)
        task_data["due_date"] = due_date
        # Ensure difficulty is stored as its value (e.g., 'easy')
        if isinstance(difficulty, Difficulty):
            task_data["difficulty"] = difficulty.value
        else:
            task_data["difficulty"] = difficulty

        # --- 3. Begin Atomic Transaction ---
        try:
            # Create the Task object
            task: Task = Task(**task_data)
            self._session.add(task)
            
            # Flush the session to add the task, but don't commit yet.
            # This makes the task available for the project status update.
            self._session.flush()

            # Call the ProjectManager to update the project's status
            # This stages the project update in the *same* transaction.
            project_update_res: dict = project_manager.update_project_status(project_id=project_id)

            # If the project update failed, we must roll back the task creation
            if not project_update_res.get("success"):
                # Raise a value error to trigger the rollback
                raise ValueError(f"Error updating project. {project_update_res.get("msg", "")}")

            # Both operations succeeded, commit the transaction.
            self._session.commit()
            return success_res(msg="Task created!", payload={})
        
        except Exception as e:
            # If anything fails (task creation or project update),
            # roll back the entire transaction.
            self._session.rollback()
            # Note: A small bug here, error message refers to 'editing'
            return error_res(f"Error creating task. Error: {e}")

    def edit_task(self, task_id, **raw_data):
        """
        Validates and updates an existing task in the database.

        Args:
            task_id (int): The ID of the task to edit.
            **raw_data: Keyword arguments for fields to update (name, due_date).

        Returns:
            dict: A standardized success or error response dictionary.
        """
        if not task_id:
            return error_res("No task id given...")
        
        task = self.get_task_by_id(task_id)

        if not task:
            return error_res("Task not found...")
        
        data_to_update = {}

        try:
            # --- 1. Validate and collect data ---
            for key, value in raw_data.items():
                # Skip any empty or None values
                if value is None or value is "":
                    continue

                if key == "name":
                    value = str(value).strip()
                    if not (5 < len(value) < 100):
                        return error_res("Invalid task name. Must be between 5 and 100 characters.")
                    data_to_update["name"] = value

                if key == "due_date":
                    # Convert date string from API to a date object
                    due_date = datetime.strptime(str(value), '%Y-%m-%d').date()
                    data_to_update["due_date"] = due_date
        
        except ValueError as e:
            # Catches the datetime.strptime() error
            return error_res(f"Invalid data provided: {e}")
        except Exception as e:
            return error_res(f"An unexpected error occurred: {e}")
        
        if not data_to_update:
            return error_res("No valid data to update...")
        
        # --- 2. Apply updates ---
        for key, value in data_to_update.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        # --- 3. Commit changes ---
        try:
            self._session.add(task)
            self._session.commit()
            return success_res(msg="Task updated!", payload={})
        except Exception as e:
            self._session.rollback()
            return error_res(f"Error updating task. Error {e}")


    def delete_task(self, task_id):
        """
        Deletes a task and updates the parent project's status in an
        atomic transaction.

        Args:
            task_id (int): The ID of the task to delete.

        Returns:
            dict: A standardized success or error response dictionary.
        """
        db_manager: DatabaseManager = self._db_manager
        project_manager: ProjectManager = db_manager.project

        if not task_id:
            return error_res("Task ID not given...")
        
        task = self.get_task_by_id(task_id=task_id)

        if not task:
            return error_res("Task not found...")
        
        try:
            # --- 1. Begin Atomic Transaction ---
            self._session.delete(task)
            
            # Flush the session to register the deletion
            self._session.flush()
            
            # --- 2. Update Project Status ---
            # Recalculate the project's status *without* this task
            project_update_res = project_manager.update_project_status(task.project_id)

            if not project_update_res.get("success", False):
                # If project update fails, roll back the task deletion
                raise ValueError("Error updating projects")
            
            # --- 3. Commit Transaction ---
            self._session.commit()
            return success_res(msg="Task deleted...", payload={})
        
        except Exception as e:
            self._session.rollback()
            return error_res(f"Error deleting task. Error: {e}")

    def get_project_tasks(self, project_id):
        """
        Gets all tasks associated with a specific project ID, ordered by due date.

        Args:
            project_id (int): The project's primary key.

        Returns:
            dict: A standardized success or error response dictionary.
        """
        if not project_id:
            return error_res("Project not given")

        try:
            # Build the query
            query = select(Task).where(
                Task.project_id == project_id
            ).order_by(Task.due_date.asc())

            tasks = self._session.scalars(query).all()

            return success_res(msg="Tasks found!", payload={ "tasks": tasks })
        except Exception as e:
            return error_res(f"Error getting tasks. Error {e}")
    
    def get_tasks_by_difficulty(self, project_id, difficulty_key):
        """
        Gets all tasks for a project, with an optional filter by difficulty.

        Args:
            project_id (int): The project's primary key.
            difficulty_key (str | None): A string key ('easy', 'medium',
                                         'hard', 'all', or None).

        Returns:
            dict: A standardized success or error response dictionary.
        """
        if not project_id:
            return error_res("Project not given")

        # Start with the base query
        query = select(Task).where(Task.project_id == project_id)

        # Add the difficulty filter if a valid one is provided
        if difficulty_key and difficulty_key != "all":
            difficulty_map = {
                "easy": Difficulty.EASY,
                "medium": Difficulty.MEDIUM,
                "hard": Difficulty.HARD,
            }
            if difficulty_key in difficulty_map:
                # Add the 'WHERE' clause for difficulty
                query = query.where(Task.difficulty == difficulty_map.get(difficulty_key))
        
        try:
            tasks = self._session.scalars(query).all()
            return success_res(msg="Tasks found!", payload={ "tasks": tasks })
        except Exception as e:
            return error_res(f"Error getting tasks. Error {e}")

    def get_task_by_id(self, task_id):
        """
        Retrieves a single task by its primary key.

        Bypasses the standardized response system for internal use.

        Args:
            task_id (int): The primary key of the task to retrieve.

        Returns:
            Task | None: The SQLAlchemy Task object if found, else None.
        """
        if not task_id:
            return None
        
        # .get() is the most efficient way to query by primary key
        return self._session.get(Task, task_id)
    
    def update_task_status(self, task_id):
        """
        Toggles a task's 'is_complete' status and updates the parent
        project's status in an atomic transaction.

        Args:
            task_id (int): The ID of the task to update.

        Returns:
            dict: A standardized success or error response dictionary.
        """
        db_manager = self._db_manager
        project_manager: ProjectManager = db_manager.project

        if not task_id:
            return error_res("Task not given...")
        
        task: Task | None = self.get_task_by_id(task_id)

        if not task:
            return error_res("Task not found...")
        
        try:
            # --- 1. Begin Atomic Transaction ---
            # Toggle the 'is_complete' status
            task.is_complete = True if not task.is_complete else False
            self._session.add(task)
            
            # Flush the session to register the change
            self._session.flush()

            # --- 2. Update Project Status ---
            # Recalculate the project's status with the new task status
            project_update_res = project_manager.update_project_status(task.project_id)

            if not project_update_res.get("success", False):
                # If project update fails, roll back the task status change
                raise ValueError("Error updating projects")
            
            # --- 3. Commit Transaction ---
            self._session.commit()
            return success_res(msg="Task updated!", payload={})
        
        except Exception as e:
            self._session.rollback()
            return error_res(f"Error updating task status tasks. Error {e}")
