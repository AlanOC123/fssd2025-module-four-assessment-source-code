from .blueprints.projects import project_bp
from .core.playground import test_route
from .core.index import main_index_route
from .core.settings import settings_route
from .blueprints.auth import auth_bp
from .blueprints.api import api_bp

ROUTES = [
    project_bp,
    auth_bp,
    api_bp,
    test_route,
    main_index_route,
    settings_route
]