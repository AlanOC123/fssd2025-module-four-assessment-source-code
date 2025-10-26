from app.helper.classes.database.ProfileManager import ProfileManager, PasswordManager
from app.database.models import Profile
from flask_login import login_user, logout_user
from app.helper.functions.response_schemas import success_res, error_res

class AuthManager:
    def __init__(self, profile_manager: ProfileManager, password_manager: PasswordManager) -> None:
        self.profile_manager: ProfileManager = profile_manager
        self.password_manager: PasswordManager = password_manager
    
    def login(self, email: str, password: str, remember=False):
        # Get the user from the database
        profile_res: dict = self.profile_manager.get_profile_by_email(email)
        is_success: bool = profile_res.get("success", False)
        payload = None

        # If not found return an error for caller to handle
        if not is_success:
            return error_res(f"Invalid Email or Password...")

        payload = profile_res.get("payload", {})
        profile: Profile = payload.get("profile")
        
        # Check password
        is_correct = self.password_manager.verify(profile.password, password)

        # If not correct return an error
        if not is_correct:
            return error_res("Invalid Email or Password...")
        
        login_user(user=profile, remember=remember)

        return success_res(payload={ "profile": profile }, msg=f"Hello {profile.first_name}!")
    
    def logout(self):
        logout_user()

