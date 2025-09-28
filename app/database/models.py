from app import db
from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone

class User(db.Model):
    __tablename__ = "users"

    # Primary Key
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)

    # Username
    user_name: Mapped[str] = mapped_column(db.String(30), nullable=False, unique=True)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, 
        default=datetime.now(timezone.utc), 
        nullable=False
    )

    # Projects
    projects: Mapped[list["Project"]] = db.relationship("Project", backref="user", lazy=False)

    # Thoughts
    thoughts: Mapped[list["Thought"]] = db.relationship("Thought", backref="user", lazy=True)

    # Theme
    theme_id: Mapped[int | None] = mapped_column(db.ForeignKey("themes.id"), nullable=True)
    is_light: Mapped[bool] = mapped_column(db.Boolean, default=True)

class Project(db.Model):
    __tablename__ = "projects"

    # Primary Key
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)

    # Owner
    owner_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"))

    # Project Name
    project_name: Mapped[str] = mapped_column(db.String(100), nullable=False)

    # Project Description
    project_description: Mapped[str | None] = mapped_column(db.String(500))

    # Created At
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, 
        default=datetime.now(timezone.utc), 
        nullable=False
    )

    # Tasks
    tasks: Mapped[list["Task"]] = db.relationship("Task", backref="project", lazy=True)

    # Status
    is_active: Mapped[bool] = mapped_column(db.Boolean, default=False)
    is_complete: Mapped[bool] = mapped_column(db.Boolean, default=False)

    def __repr__(self) -> str:
        return f"ID: {self.id}\nProject Name: {self.project_name}"

class Task(db.Model):
    __tablename__ = "tasks"

    # Primary Key
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)

    # Task Name
    task_name: Mapped[str] = mapped_column(db.String(100), nullable=False)

    # Created At
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, 
        default=datetime.now(timezone.utc), 
        nullable=False
    )

    # Related Project
    project_id: Mapped[int] = mapped_column(db.ForeignKey("projects.id"))

    # Status
    is_complete: Mapped[bool] = mapped_column(db.Boolean, default=False)

    def __repr__(self) -> str:
        return f"ID: {self.id}\nTask Name: {self.task_name}"

class Thought(db.Model):
    __tablename__ = "thoughts"

    # Primary Key
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)

    # Owner
    owner_id: Mapped[int] = mapped_column(db.ForeignKey("users.id"))

    # Thought Name
    thought_title: Mapped[str] = mapped_column(db.String(30), nullable=False)

    # Thought Content
    thought_content: Mapped[str] = mapped_column(db.String(200), nullable=False)

    # Created At
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, 
        default=datetime.now(timezone.utc), 
        nullable=False
    )

    def __repr__(self) -> str:
        return f"ID: {self.id}\nTask Name: {self.thought_title}"

class Theme(db.Model):
    __tablename__ = "themes"

    # Primary Key
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)

    # Theme Name
    theme_name: Mapped[str] = mapped_column(db.String(30), unique=True)

    # Primary Color
    pri_clr = mapped_column(db.String(7))

    # Secondary Color
    sec_clr = mapped_column(db.String(7))

    # Accent Color
    acc_clr = mapped_column(db.String(7))

    # Text Color
    text_clr = mapped_column(db.String(7))

    def __repr__(self) -> str:
        return f"ID: {self.id}\nTask Name: {self.theme_name}"

# Reset DB State
def reset_tables(app):
    with app.app_context():
        # Drop Existing DB Tables
        db.drop_all()

        # Recreate them
        db.create_all()

    from .seed import seed_initial_user

    # Run test user insertion script
    seed_initial_user(app)
