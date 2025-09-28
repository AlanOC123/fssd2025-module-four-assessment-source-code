from .blueprints.projects import project_bp
from .core.playground import test_route
from .blueprints.auth import auth_bp

ROUTES = [
    project_bp,
    auth_bp,
    test_route
]