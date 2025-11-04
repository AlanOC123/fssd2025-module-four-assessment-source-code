from .BaseManager import BaseManager
from .ProjectManager import ProjectManager
from app.database.models import Task, Difficulty, Project
from app.helper.functions.response_schemas import success_res, error_res
from datetime import date, timedelta, datetime
from sqlalchemy import select

class TaskManager(BaseManager):
    def __init__(self, db_manager_instance) -> None:
        super().__init__(db_manager_instance)

    def create_task(self, **raw_data):
        from .DatabaseManager import DatabaseManager
        db_manager: DatabaseManager = self._db_manager
        project_manager: ProjectManager = db_manager.project

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
        
        task_data["name"] = str(name).strip()
        task_data["project_id"] = int(project_id)
        task_data["due_date"] = due_date
        task_data["difficulty"] = difficulty.value

        try:
            task: Task = Task(**task_data)
            self._session.add(task)
            self._session.flush()

            project_update_res: dict = project_manager.update_project_status(project_id=project_id)

            if not project_update_res.get("success"):
                raise ValueError(f"Error updating project. {project_update_res.get("msg", "")}")

            self._session.commit()
            return success_res(msg="Task created!", payload={})
        except Exception as e:
            self._session.rollback()
            return error_res(f"Error editing task. Error: {e}")

    def edit_task(self, **raw_data):
        pass

    def delete_task(self, task_id):
        if not task_id:
            return error_res("Task ID not given...")
        
        task = self.get_task_by_id(task_id=task_id)

        if not task:
            return error_res("Task not found...")
        
        try:
            self._session.delete(task)
            self._session.commit()
            return success_res(msg="Task deleted...", payload={})
        except Exception as e:
            self._session.rollback()
            return error_res(f"Error deleting task. Error: {e}")

    def get_project_tasks(self, project_id):
        if not project_id:
            return error_res("Project not given")

        try:
            query = select(Task).where(
                Task.project_id == project_id
            ).order_by(Task.due_date.asc())

            tasks = self._session.scalars(query).all()

            return success_res(msg="Tasks found!", payload={ "tasks": tasks })
        except Exception as e:
            return error_res(f"Error getting tasks. Error {e}")
    
    def get_tasks_by_difficulty(self, project_id, difficulty_key):
        if not project_id:
            return error_res("Project not given")

        query = select(Task).where(Task.project_id == project_id)

        if difficulty_key and difficulty_key != "all":
            difficulty_map = {
                "easy": Difficulty.EASY,
                "medium": Difficulty.MEDIUM,
                "hard": Difficulty.HARD,
            }

            if difficulty_key in difficulty_map:
                query = query.where(Task.difficulty == difficulty_map.get(difficulty_key))
        
        try:
            tasks = self._session.scalars(query).all()
            return success_res(msg="Tasks found!", payload={ "tasks": tasks })
        except Exception as e:
            return error_res(f"Error getting tasks. Error {e}")

    def get_task_by_id(self, task_id):
        if not task_id:
            return None
        
        return self._session.get(Task, task_id)
    
    def update_task_status(self, task_id, project_id, new_status):
        db_manager: DatabaseManager = self._db_manager
        project_manager: ProjectManager = db_manager.project

        if not task_id:
            return error_res("Task not given...")

        if not project_id:
            return error_res("Project not given...")
        
        task: Task | None = self.get_task_by_id(task_id)

        if not task:
            return error_res("Task not found...")
        
        try:
            task.is_complete = new_status
            self._session.add(task)
            self._session.flush()
            project_update_res = project_manager.update_project_status(task.project_id)

            if not project_update_res.get("success", False):
                raise ValueError("Error updating projects")
            
            self._session.commit()
        except Exception as e:
            self._session.rollback()
            return error_res(f"Error updating task status tasks. Error {e}")
