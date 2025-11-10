"""
Defines all SQLAlchemy database models and Enums for the application.

This file is the "single source of truth" for the database schema.
Each class defined here maps to a table in the PostgreSQL database.
The models define all columns, relationships, and custom helper
properties for accessing and manipulating data.
"""

import enum
from app import db
from sqlalchemy import Boolean, Enum, String, Integer, Date, ForeignKey, Text, desc
from typing import List
from sqlalchemy import cast
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from flask_login import UserMixin
from datetime import date

# --- Enums ---
# These enums are used to define strict, allowed values for certain columns.
# Using 'native_enum=True' in the models makes PostgreSQL store these as
# native ENUM types, which is very efficient.

class ThemeMode(enum.Enum):
    """Defines the allowed display modes for the theme system."""
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"

class Status(enum.Enum):
    """Defines the allowed statuses for a Project."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class Difficulty(enum.Enum):
    """Defines the allowed difficulty levels for a Task."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD ="hard"

# --- Models ---

class Profile(db.Model, UserMixin):
    """
    Represents a User/Profile in the database.
    
    This is the central model for a user, containing their personal details,
    account credentials, and theme preferences. It inherits from 'UserMixin'
    to provide the methods required by Flask-Login (e.g., is_authenticated).
    """
    __tablename__ = "profiles"

    # Personal
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    surname: Mapped[str] = mapped_column(String(80), nullable=False)
    date_of_birth: Mapped[Date] = mapped_column(Date, nullable=False)

    # Account
    email: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    stay_logged_in: Mapped[Boolean] = mapped_column(Boolean, default=False)

    # Theme
    theme_id: Mapped[int] = mapped_column(ForeignKey("themes.id"))
    theme_mode: Mapped[ThemeMode] = mapped_column(
        Enum(ThemeMode),
        default=ThemeMode.SYSTEM,
        nullable=False
    )

    # --- Relationships ---
    
    # 'cascade="all, delete-orphan"' means that when a Profile is deleted,
    # all of its related 'ProfileIdentity', 'Project', and 'Thought'
    # objects will be automatically deleted from the database.
    
    # 'lazy="selectin"' is a performance optimization. When a Profile is
    # loaded, it will load its 'identities' in a single, separate query
    # (using a 'SELECT ... WHERE profile_id IN (...)'), which avoids
    # the "N+1 problem" of lazy="select".
    identities: Mapped[List["ProfileIdentity"]] = relationship(
        back_populates="profile", cascade="all, delete-orphan", lazy="selectin"
    )
    projects: Mapped[List["Project"]] = relationship(
        back_populates="profile", cascade="all, delete-orphan", lazy="select"
    )
    thoughts: Mapped[List["Thought"]] = relationship(
        back_populates="profile", cascade="all, delete-orphan", lazy="select"
    )
    
    # 'lazy="joined"' means that when a Profile is loaded, SQLAlchemy
    # will perform a SQL JOIN to fetch the 'Theme' object in the *same*
    # query. This is efficient because a Profile only has one Theme.
    theme: Mapped["Theme"] = relationship(lazy="joined")
    
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, 
        default=datetime.now(timezone.utc), 
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<Profile {self.email}>"
    
class ProfileIdentity(db.Model):
    """
    Represents a user's specific "Identity" (e.g., "The Learner").
    
    This is the core of the app. It's a link table that connects a
    'Profile' (the user) to an 'IdentityTemplate' (the base identity).
    It also stores the 'custom_name' and whether it's the 'is_active'
    identity for the user.
    """
    __tablename__ = "profile_identities"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey('profiles.id'))
    template_id: Mapped[int] = mapped_column(ForeignKey('identity_templates.id'))
    is_active: Mapped[Boolean] = mapped_column(Boolean, default=False)
    custom_name: Mapped[str] = mapped_column(String(30), nullable=True)

    # --- Relationships ---
    profile: Mapped["Profile"] = relationship(
        back_populates="identities"
    )
    
    # When a ProfileIdentity is deleted, all its associated Projects
    # and Thoughts are also deleted.
    projects: Mapped[List["Project"]] = relationship(
        back_populates='profile_identity', cascade="all, delete-orphan", lazy="select"
    )
    
    # The 'template' is lazy="joined" because an Identity always
    # needs to know its template's name and image.
    template: Mapped["IdentityTemplate"] = relationship(
        back_populates='profile_identities', lazy="joined"
    )
    
    thoughts: Mapped[List["Thought"]] = relationship(
        back_populates="profile_identity", 
        cascade="all, delete-orphan", 
        lazy="select",
        order_by="desc(Thought.created_at)" # Thoughts page shows newest first
    )
    
    identity_created_at: Mapped[datetime] = mapped_column(
        db.DateTime, 
        default=datetime.now(timezone.utc), 
        nullable=False
    )

    def __repr__(self) -> str:
        return f'<Profile Identity {self.id}>'


class IdentityTemplate(db.Model):
    """
    Represents the template for an Identity (e.g., "The Learner").
    
    This table stores the *base* properties of an identity, like its
    default name, description, and avatar image. It is seeded from
    'identities.json'.
    """
    __tablename__ = "identity_templates"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255))
    image: Mapped[str] = mapped_column(String(120), nullable=False)
    
    profile_identities: Mapped[List["ProfileIdentity"]] = relationship(
        back_populates="template",
        lazy="select"
    )
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, 
        default=datetime.now(timezone.utc), 
        nullable=False
    )

    def __repr__(self) -> str:
        return f'<Identity {self.name}>'


class Project(db.Model):
    """
    Represents a single Project.
    
    A project is owned by both a 'Profile' (the user) and a
    'ProfileIdentity' (the workspace). It contains a list of tasks.
    """
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"))
    identity_id: Mapped[int] = mapped_column(
        db.ForeignKey("profile_identities.id")
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[Boolean] = mapped_column(Boolean, default=False)
    description: Mapped[str | None] = mapped_column(Text)
    
    # --- Relationships ---
    profile: Mapped["Profile"] = relationship(
        back_populates="projects", lazy="select"
    )
    profile_identity: Mapped["ProfileIdentity"] = relationship(
        back_populates="projects"
    )
    
    # 'lazy="selectin"' is a key performance optimization here.
    # When a Project is loaded, all its Tasks are loaded in one
    # go. This is crucial for the 'tasks_completed_percentage'
    # property to work without N+1 queries.
    tasks: Mapped[List["Task"]] = relationship(
        back_populates="project", 
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    end_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    
    # Uses a native PostgreSQL ENUM for the 'status' column.
    status: Mapped[Status] = mapped_column(
        Enum(
            Status, 
            native_enum=True, # Use PG ENUM
            values_callable=lambda obj: [e.value for e in obj]
        ),
        default=Status.NOT_STARTED,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, 
        default=datetime.now(timezone.utc), 
        nullable=False
    )

    @property
    def is_overdue(self) -> bool:
        """Checks if the project is past its end_date and not completed."""
        if not self.end_date:
            return False
        
        return (self.status != Status.COMPLETED and self.end_date < date.today())

    def __repr__(self) -> str:
        return f"<Project {self.name}>"
    
    @property
    def time_elapsed_percentage(self):
        """
        Calculates what percentage of the project's *time* has passed.
        (e.g., 50% if 10 days have passed on a 20-day project).
        """
        today = date.today()
        if self.status == Status.COMPLETED:
            return 100
        
        # If project hasn't started, or dates are missing, 0%
        if not self.start_date or not self.end_date or self.start_date > today:
            return 0
        
        total_duration = (self.end_date - self.start_date).days
        if total_duration == 0:
            # Avoid ZeroDivisionError if start and end are same day
            return 100

        elapsed_duration = (today - self.start_date).days
        percentage = elapsed_duration / total_duration * 100

        # Clamp value between 0 and 100
        return int(min(max(percentage, 0), 100))
    
    @property
    def time_left(self):
        """Calculates the number of days remaining until the end_date."""
        today = date.today()
        if self.status == Status.COMPLETED:
            return 0
        
        if not self.end_date:
            return 0
        
        if self.end_date < today:
            return 0
        
        days_remaining = (self.end_date - today).days

        return days_remaining

    @property
    def tasks_completed_percentage(self):
        """
        Calculates what percentage of the project's *tasks* are complete.
        
        This relies on the 'tasks' relationship being loaded via 'lazy="selectin"'.
        """
        if self.status == Status.COMPLETED:
            return 100
        
        if not len(self.tasks):
            return 0
        
        # Count tasks where task.is_complete is True
        tasks_completed = [task for task in self.tasks if task.is_complete]

        percentage = float((len(tasks_completed) / len(self.tasks)) * 100)

        return float(min(max(percentage, 0), 100))

    @property
    def tasks_incomplete(self):
        """Counts the number of tasks that are not complete."""
        if self.status == Status.COMPLETED:
            return 0 # Changed this from len(self.tasks) to be more intuitive

        if not len(self.tasks):
            return 0

        total_tasks = len(self.tasks)
        tasks_incompleted = len([task for task in self.tasks if not task.is_complete])

        return int(min(max(tasks_incompleted, 0), total_tasks))

    @property
    def total_tasks(self):
        """Returns the total number of tasks for this project."""
        return len(self.tasks)


class Task(db.Model):
    """
    Represents a single Task.
    
    A task belongs to one Project. Its 'difficulty' is stored as a
    native PostgreSQL ENUM.
    """
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    difficulty: Mapped[Difficulty] = mapped_column(
        Enum(
            Difficulty, 
            native_enum=True,
            name="difficulty",
            values_callable=lambda obj: [e.value for e in obj]
        ),
        default=Difficulty.MEDIUM.value,
        nullable=False
    )
    
    is_complete: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # 'lazy="joined"' is a good choice here, as a Task almost
    # always needs to know its parent Project's info.
    project: Mapped["Project"] = relationship(
        back_populates="tasks",
        lazy="joined"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, 
        default=datetime.now(timezone.utc), 
        nullable=False
    )

    @property
    def time_left(self):
        """Calculates the number of days remaining until the due_date."""
        if not self.due_date:
            return 0
        
        today = date.today()
        days_remaining = (self.due_date - today).days

        # A task can have negative days (overdue), but we'll show 0
        return max(days_remaining, 0)

    @property
    def time_elapsed_percentage(self):
        """
        Calculates what percentage of the task's *time* has passed
        (from creation to due date).
        """
        today = date.today()
        start = self.created_at.date() # Get the date part of the creation timestamp

        if self.is_complete:
            return 100
        if not self.due_date:
            return 100
        
        # Handle edge cases
        if self.due_date < start:
            return 100
        if today < start:
            return 0
        if today >= self.due_date:
            return 100

        # Calculate percentage
        elapsed = (today - start).days
        total = (self.due_date - start).days
        if total == 0:
            return 100

        percentage = (elapsed / total) * 100

        return int(min(max(percentage, 0), 100))

    def __repr__(self) -> str:
        return f"<Task {self.name}>"

class Thought(db.Model):
    """
    Represents a single Thought entry in the journal.
    
    A thought is owned by both a 'Profile' and a 'ProfileIdentity'.
    """
    __tablename__ = "thoughts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"))
    profile_identity_id: Mapped[int] = mapped_column(ForeignKey("profile_identities.id"))

    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # 'lazy="joined"' is efficient as a thought's content is
    # almost always displayed with its profile/identity.
    profile: Mapped["Profile"] = relationship(
        back_populates="thoughts",
        lazy="joined"
    )
    profile_identity: Mapped["ProfileIdentity"] = relationship(
        back_populates="thoughts",
        lazy="joined",
        order_by="desc(Thought.created_at)"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, 
        default=datetime.now(timezone.utc), 
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<Thought {self.id}>"

class Theme(db.Model):
    """
    Represents a color theme.
    
    This table stores the HSL hue values for a theme, which are
    injected as CSS variables to dynamically style the frontend.
    It is seeded from 'themes.json'.
    """
    __tablename__ = "themes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)
    is_default: Mapped[Boolean] = mapped_column(Boolean, default=False, nullable=False)
    primary_hue: Mapped[int] = mapped_column(Integer)
    secondary_hue: Mapped[int] = mapped_column(Integer)
    tertiary_hue: Mapped[int] = mapped_column(Integer)
    neutral_hue: Mapped[int] = mapped_column(Integer)
    text_hue: Mapped[int] = mapped_column(Integer)

    def __repr__(self) -> str:
        return f"<Theme {self.name}>"
