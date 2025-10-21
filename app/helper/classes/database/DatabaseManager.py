from flask import Flask
from .BaseManager import BaseManager
from .ProfileManager import ProfileManager, PasswordManager
from .IdentityTemplateManager import IdentityTemplateManager
from .ProfileIdentityManager import ProfileIdentityManager
from .ThemeManager import ThemeManager

class DatabaseManager(BaseManager):
    def __init__(self, config) -> None:
        super().__init__(self)
        self._profile_manager = ProfileManager(self, PasswordManager(config))
        self._identity_template_manager = IdentityTemplateManager(self)
        self._profile_identity_manager = ProfileIdentityManager(self)
        self._theme_manager = ThemeManager(self)

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
    def theme(self) -> ThemeManager:
        return self._theme_manager