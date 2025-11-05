import enum
from app import db
from sqlalchemy import Boolean, Enum, String, Integer, Date, ForeignKey, Text, desc
from typing import List
from sqlalchemy import cast
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from flask_login import UserMixin
from datetime import date

class ThemeMode(enum.Enum):
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"

class Status(enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class Difficulty(enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD ="hard"

class Profile(db.Model, UserMixin):
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

    identities: Mapped[List["ProfileIdentity"]] = relationship(
        back_populates="profile", cascade="all, delete-orphan", lazy="selectin"
    )
    projects: Mapped[List["Project"]] = relationship(
        back_populates="profile", cascade="all, delete-orphan", lazy="select"
    )
    thoughts: Mapped[List["Thought"]] = relationship(
        back_populates="profile", cascade="all, delete-orphan", lazy="select"
    )
    theme: Mapped["Theme"] = relationship(lazy="joined")
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, 
        default=datetime.now(timezone.utc), 
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<Profile {self.email}>"
    
class ProfileIdentity(db.Model):
    __tablename__ = "profile_identities"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey('profiles.id'))
    template_id: Mapped[int] = mapped_column(ForeignKey('identity_templates.id'))
    is_active: Mapped[Boolean] = mapped_column(Boolean, default=False)
    custom_name: Mapped[str] = mapped_column(String(30), nullable=True)

    profile: Mapped["Profile"] = relationship(
        back_populates="identities"
    )
    projects: Mapped[List["Project"]] = relationship(
        back_populates='profile_identity', cascade="all, delete-orphan", lazy="select"
    )
    template: Mapped["IdentityTemplate"] = relationship(
        back_populates='profile_identities', lazy="joined"
    )
    thoughts: Mapped[List["Thought"]] = relationship(
        back_populates="profile_identity", 
        cascade="all, delete-orphan", 
        lazy="select",
        order_by="desc(Thought.created_at)"
    )
    identity_created_at: Mapped[datetime] = mapped_column(
        db.DateTime, 
        default=datetime.now(timezone.utc), 
        nullable=False
    )

    def __repr__(self) -> str:
        return f'<Profile Identity {self.id}>'


class IdentityTemplate(db.Model):
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
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"))
    identity_id: Mapped[int] = mapped_column(
        db.ForeignKey("profile_identities.id")
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[Boolean] = mapped_column(Boolean, default=False)
    description: Mapped[str | None] = mapped_column(Text)
    profile: Mapped["Profile"] = relationship(
        back_populates="projects", lazy="select"
    )

    profile_identity: Mapped["ProfileIdentity"] = relationship(
        back_populates="projects"
    )

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

    status: Mapped[Status] = mapped_column(
        Enum(
            Status, 
            native_enum=True,
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
        if not self.end_date:
            return False
        
        return (self.status != Status.COMPLETED and self.end_date < date.today())

    def __repr__(self) -> str:
        return f"<Project {self.name}>"
    
    @property
    def time_elapsed_percentage(self):
        today = date.today()
        if self.status == Status.COMPLETED:
            return 100
        
        if not self.start_date or not self.end_date or self.start_date > today:
            return 0
        
        total_duration = (self.end_date - self.start_date).days

        if total_duration == 0:
            return 100

        elapsed_duration = (today - self.start_date).days
        percentage = elapsed_duration / total_duration * 100

        return int(min(max(percentage, 0), 100))
    
    @property
    def time_left(self):
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
        if self.status == Status.COMPLETED:
            return 100
        
        if not len(self.tasks):
            return 0
        
        tasks_completed = [task.is_complete for task in self.tasks]

        percentage = (len(tasks_completed) / len(self.tasks))

        return int(min(max(percentage, 0), 100))

    @property
    def tasks_incomplete(self):
        if self.status == Status.COMPLETED:
            return len(self.tasks)

        if not len(self.tasks):
            return 0

        total_tasks = len(self.tasks)
        tasks_incompleted = len([not task.is_complete for task in self.tasks])

        return int(min(max(tasks_incompleted, 0), total_tasks))

    @property
    def total_tasks(self):
        return len(self.tasks)


class Task(db.Model):
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
        if not self.due_date:
            return 0
        
        today = date.today()

        days_remaining = (self.due_date - today).days

        return max(days_remaining, 0)

    @property
    def time_elapsed_percentage(self):
        
        today = date.today()
        start = self.created_at.date()

        if self.is_complete:
            return 100
        if not self.due_date:
            return 100
        
        if self.due_date < start:
            return 100
        if today < start:
            return 0
        if today >= self.due_date:
            return 100

        elapsed = (today - start).days
        total = (self.due_date - start).days

        if total == 0:
            return 100

        percentage = (elapsed / total) * 100

        return int(min(max(percentage, 0), 100))

    def __repr__(self) -> str:
        return f"<Task {self.name}>"
class Thought(db.Model):
    __tablename__ = "thoughts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"))
    profile_identity_id: Mapped[int] = mapped_column(ForeignKey("profile_identities.id"))

    content: Mapped[str] = mapped_column(Text, nullable=False)
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
