import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DefaultConfig():
    # 1. Load Secret Key
    SECRET_KEY = os.environ.get("SECRET_KEY") or "unsecure_dev_key"

    # 2. Disable change tracking to reduce overhead
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 3. Declare Metadata
    SITE_NAME = "Projectify"
    SITE_TAGLINE = "Organise Thoughts into Actions"
class ProductionConfig(DefaultConfig):
    # 1. Load Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL_PROD")

    # 2. Declare test state
    TESTING = False
class TestingConfig(DefaultConfig):
    # 1. Load Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL_TEST")

    # 2. Declare test state
    TESTING = True

config = {
    "default": DefaultConfig,
    "production": ProductionConfig,
    "testing": TestingConfig
}

DEFAULT = DefaultConfig