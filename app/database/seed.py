from app import db
from .models import User

def _create_user(app):
    # Get the current app
    with app.app_context():
        # Check for duplicates
        users_exists = db.session.execute(
            db.select(User).filter_by(user_name="AdminUser")
        ).scalar_one_or_none() or False

        if not users_exists:
            # Create the user
            admin_user = User(user_name="AdminUser")
            db.session.add(admin_user)
            db.session.commit()
            print("Admin User Set Up Correctly")
        else:
            # Indicate presence
            print("Admin already created")

def seed_initial_user(app):
    _create_user(app)