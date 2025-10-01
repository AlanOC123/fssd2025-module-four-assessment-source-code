from flask import Flask
from .BaseManager import BaseManager
from .UserManager import UserManager

class DatabaseManager(BaseManager):
    _user_manager: UserManager | None = None
    def __init__(self, app: Flask) -> None:
        super().__init__(app)
        self._user_manager = UserManager(app)
    
    @property
    def user(self):
        return self._user_manager