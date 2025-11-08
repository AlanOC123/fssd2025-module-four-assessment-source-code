"""
Defines the DatabaseManager, the central access point for all managers.

This file initializes the main DatabaseManager class, which acts as a
service locator or facade. It instantiates all other specific database
managers (e.g., ProfileManager, ProjectManager) and provides them
to the rest of the application, often via the Flask 'app' context
(e.g., 'current_app.db_manager.profile').
"""

from flask import Flask
from .BaseManager import BaseManager
from .ProfileManager import ProfileManager, PasswordManager
from .IdentityTemplateManager import IdentityTemplateManager
from .ProfileIdentityManager import ProfileIdentityManager
from .ThemeManager import ThemeManager
from .ThoughtManager import ThoughtManager
from .ProjectManager import ProjectManager
from .TaskManager import TaskManager

class DatabaseManager(BaseManager):
    """
    Manages all database manager instances for the application.

    This class inherits from BaseManager to get access to the session
    and cache. Its primary role is to initialize and hold instances of all
    other managers, making them accessible via properties. This follows
    the Facade design pattern, simplifying access to the data layer.
    """
    def __init__(self, config) -> None:
        """
        Initializes the DatabaseManager and all child manager instances.

        Args:
            config (dict): The Flask application config object, required
                           by the PasswordManager for password settings.
        """
        super().__init__(self)
        
        # Initialize all specific managers, passing 'self' (the DatabaseManager)
        # to them. This allows managers to access each other
        # (e.g., TaskManager can access ProjectManager via self._db_manager.project).
        self._profile_manager = ProfileManager(self, PasswordManager(config))
        self._identity_template_manager = IdentityTemplateManager(self)
        self._profile_identity_manager = ProfileIdentityManager(self)
        self._thought_manager = ThoughtManager(self)
        self._theme_manager = ThemeManager(self)
        self._project_manager = ProjectManager(self)
        self._task_manager = TaskManager(self)

    @property
    def profile(self) -> ProfileManager:
        """
        Provides access to the ProfileManager instance.

        Returns:
            ProfileManager: The manager for Profile and Password operations.
        """
        return self._profile_manager
    
    @property
    def identity_template(self) -> IdentityTemplateManager:
        """
        Provides access to the IdentityTemplateManager instance.

        Returns:
            IdentityTemplateManager: The manager for identity templates.
        """
        return self._identity_template_manager
    
    @property
    def profile_identity(self) -> ProfileIdentityManager:
        """
        Provides access to the ProfileIdentityManager instance.

        Returns:
            ProfileIdentityManager: The manager for user-specific identities.
        """
        return self._profile_identity_manager
    
    @property
    def thought(self) -> ThoughtManager:
        """
        Provides access to the ThoughtManager instance.

        Returns:
            ThoughtManager: The manager for Thought operations.
        """
        return self._thought_manager

    @property
    def theme(self) -> ThemeManager:
        """
        Provides access to the ThemeManager instance.

        Returns:
            ThemeManager: The manager for Theme operations.
        """
        return self._theme_manager
    
    @property
    def project(self) -> ProjectManager:
        """
        Provides access to the ProjectManager instance.

        Returns:
            ProjectManager: The manager for Project operations.
        """
        return self._project_manager
    
    @property
    def task(self) -> TaskManager:
        """
        Provides access to the TaskManager instance.

        Returns:
            TaskManager: The manager for Task operations.
        """
        return self._task_manager