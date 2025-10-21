from app import db
from sqlalchemy import Boolean
from typing import List
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone

class Profile(db.Model):
    __tablename__ = "profiles"
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(db.String(50), nullable=False)
    surname: Mapped[str] = mapped_column(db.String(80), nullable=False)
    date_of_birth: Mapped[datetime.date] = mapped_column(db.Date, nullable=False)
    email: Mapped[str] = mapped_column(db.String(50), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(db.String(128), nullable=False)
    theme_id: Mapped[int] = mapped_column(db.ForeignKey("themes.id"))
    stay_logged_in: Mapped[Boolean] = mapped_column(db.Boolean, default=False)
    identities: Mapped[List["ProfileIdentity"]] = db.relationship(
        back_populates="profile", cascade="all, delete-orphan", lazy="selectin"
    )
    projects: Mapped[List["Project"]] = db.relationship(
        back_populates="profile", cascade="all, delete-orphan", lazy="select"
    )
    thoughts: Mapped[List["Thought"]] = db.relationship(
        back_populates="profile", cascade="all, delete-orphan", lazy="select"
    )
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, 
        default=datetime.now(timezone.utc), 
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<Profile {self.email}>"
    
class ProfileIdentity(db.Model):
    __tablename__ = "profile_identities"
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    profile_id: Mapped[int] = mapped_column(db.ForeignKey('profiles.id'))
    template_id: Mapped[int] = mapped_column(db.ForeignKey('identity_templates.id'))
    is_active: Mapped[Boolean] = mapped_column(db.Boolean, default=False)
    custom_name: Mapped[str] = mapped_column(db.String(30), nullable=True)
    profile: Mapped["Profile"] = db.relationship(
        back_populates="identities"
    )
    projects: Mapped[List["Project"]] = db.relationship(
        back_populates='profile_identity', cascade="all, delete-orphan", lazy="select"
    )
    template: Mapped["IdentityTemplate"] = db.relationship(
        back_populates='profile_identities', lazy="joined"
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
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(80), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(db.String(255))
    image: Mapped[str] = mapped_column(db.String(120), nullable=False)
    profile_identities: Mapped[List["ProfileIdentity"]] = db.relationship(
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
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(db.ForeignKey("profiles.id"))
    identity_id: Mapped[int] = mapped_column(
        db.ForeignKey("profile_identities.id")
    )
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(db.String(500))
    profile: Mapped["Profile"] = db.relationship(
        back_populates="projects", lazy="select"
    )
    thoughts: Mapped[List["Thought"]] = db.relationship(
        back_populates="project",
        cascade="all, delete-orphan", # ADDED: Ensures thoughts are deleted with the project
        lazy="select"
    )

    profile_identity: Mapped["ProfileIdentity"] = db.relationship(
        back_populates="projects"
    )

    tasks: Mapped[List["Task"]] = db.relationship(
        back_populates="project", 
        cascade="all, delete-orphan", # ADDED: Ensures tasks are deleted with the project
        lazy="selectin"
    )
    is_active: Mapped[Boolean] = mapped_column(db.Boolean, default=False)
    is_complete: Mapped[Boolean] = mapped_column(db.Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, 
        default=datetime.now(timezone.utc), 
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<Project {self.name}>"

class Task(db.Model):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    project_id: Mapped[int] = mapped_column(db.ForeignKey("projects.id"))
    is_complete: Mapped[bool] = mapped_column(db.Boolean, default=False)
    project: Mapped["Project"] = db.relationship(
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
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(db.ForeignKey("profiles.id"))
    project_id: Mapped[int] = mapped_column(db.ForeignKey("projects.id"))
    title: Mapped[str] = mapped_column(db.String(30), nullable=False)
    content: Mapped[str] = mapped_column(db.String(200), nullable=False)
    profile: Mapped["Profile"] = db.relationship(
        back_populates="thoughts",
        lazy="joined"
    )
    project: Mapped["Project"] = db.relationship(
        back_populates="thoughts",
        lazy="joined"
    )
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, 
        default=datetime.now(timezone.utc), 
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<Thought {self.title}>"
class Theme(db.Model):
    __tablename__ = "themes"
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(30), unique=True)
    is_default: Mapped[Boolean] = mapped_column(db.Boolean, default=False, nullable=False)
    bg_base_light: Mapped [str] = mapped_column(db.String(7), nullable=False)
    bg_alt_light: Mapped [str] = mapped_column(db.String(7), nullable=False)
    acc_base_light: Mapped [str] = mapped_column(db.String(7), nullable=False)
    acc_alt_light: Mapped [str] = mapped_column(db.String(7), nullable=False)
    text_base_light: Mapped [str] = mapped_column(db.String(7), nullable=False)
    text_alt_light: Mapped [str] = mapped_column(db.String(7), nullable=False)
    success_light: Mapped [str] = mapped_column(db.String(7), nullable=False)
    warning_light: Mapped [str] = mapped_column(db.String(7), nullable=False)
    failure_light: Mapped [str] = mapped_column(db.String(7), nullable=False)
    bg_base_dark: Mapped [str] = mapped_column(db.String(7), nullable=False)
    bg_alt_dark: Mapped [str] = mapped_column(db.String(7), nullable=False)
    acc_base_dark: Mapped [str] = mapped_column(db.String(7), nullable=False)
    acc_alt_dark: Mapped [str] = mapped_column(db.String(7), nullable=False)
    text_base_dark: Mapped [str] = mapped_column(db.String(7), nullable=False)
    text_alt_dark: Mapped [str] = mapped_column(db.String(7), nullable=False)
    success_dark: Mapped [str] = mapped_column(db.String(7), nullable=False)
    failure_dark: Mapped [str] = mapped_column(db.String(7), nullable=False)
    warning_dark: Mapped [str] = mapped_column(db.String(7), nullable=False)

    def __repr__(self) -> str:
        return f"<Theme {self.name}>"
