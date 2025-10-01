from app import db
from .models import User
import bcrypt

def _create_user(app):
    # Get the current app
    with app.app_context():
        # Check for duplicates
        users_exists = db.session.execute(
            db.select(User).filter_by(user_name="TestUser")
        ).scalar_one_or_none() or False

        if not users_exists:
            # Create the user
            bytes = "password".encode("utf-8")
            salt = bcrypt.gensalt()
            pw_hash = bcrypt.hashpw(bytes, salt)
            admin_user = User(user_name="TestUser", password_hash=pw_hash)
            db.session.add(admin_user)
            db.session.commit()
            print("Test User Set Up Correctly")
        else:
            # Indicate presence
            print("Test already created")

def seed_initial_user(app):
    _create_user(app)