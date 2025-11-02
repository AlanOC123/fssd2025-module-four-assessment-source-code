import enum
from app import db
from sqlalchemy import Boolean, Enum, String, Integer, Date, ForeignKey, Text, desc
from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from flask_login import UserMixin

class ThemeMode(enum.Enum):
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"

class Status(enum.Enum):
    OVERDUE = "overdue"
    NOT_STARTED = "not-started",
    IN_PROGRESS = "in-progress",
    COMPLETED = "completed"

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
    description: Mapped[str | None] = mapped_column(String(500))
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
    is_active: Mapped[Boolean] = mapped_column(Boolean, default=False)
    is_complete: Mapped[Boolean] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, 
        default=datetime.now(timezone.utc), 
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<Project {self.name}>"

class Task(db.Model):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
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
