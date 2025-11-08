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
    Core manager for centalised database operations
    """
    def __init__(self, config) -> None:
        super().__init__(self)
        self._profile_manager = ProfileManager(self, PasswordManager(config))
        self._identity_template_manager = IdentityTemplateManager(self)
        self._profile_identity_manager = ProfileIdentityManager(self)
        self._thought_manager = ThoughtManager(self)
        self._theme_manager = ThemeManager(self)
        self._project_manager = ProjectManager(self)
        self._task_manager = TaskManager(self)

    # Attach managers as properties for easy access
    @property
    def profile(self) -> ProfileManager:
        return self._profile_manager
    
    @property
    def identity_template(self) -> IdentityTemplateManager:
        return self._identity_template_manager
    
    @property
    def profile_identity(self) -> ProfileIdentityManager:
        return self._profile_identity_manager
    
    @property
    def thought(self) -> ThoughtManager:
        return self._thought_manager

    @property
    def theme(self) -> ThemeManager:
        return self._theme_manager
    
    @property
    def project(self) -> ProjectManager:
        return self._project_manager
    
    @property
    def task(self) -> TaskManager:
        return self._task_manager