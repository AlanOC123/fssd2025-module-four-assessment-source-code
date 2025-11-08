"""
Defines the AuthManager for handling user session logic.

This file contains the AuthManager class, which acts as a facade
to orchestrate the login and logout processes. It uses the
ProfileManager to find and verify users and then uses Flask-Login's
functions to manage the user's session.
"""

from app.helper.classes.database.ProfileManager import ProfileManager, PasswordManager
from app.database.models import Profile
from flask_login import login_user, logout_user
from app.helper.functions.response_schemas import success_res, error_res

class AuthManager:
    """
    Manages the authentication logic (login/logout) for the application.

    This class coordinates between the ProfileManager (to find users)
    and the PasswordManager (to verify passwords), and then calls
    Flask-Login's `login_user` and `logout_user` functions to
    manage the actual session.
    """
    def __init__(self, profile_manager: ProfileManager, password_manager: PasswordManager) -> None:
        """
        Initializes the AuthManager.

        Args:
            profile_manager (ProfileManager): An instance of the ProfileManager
                                              for user lookups.
            password_manager (PasswordManager): An instance of the PasswordManager
                                                for password verification.
        """
        self.profile_manager: ProfileManager = profile_manager
        self.password_manager: PasswordManager = password_manager
    
    def login(self, email: str, password: str, remember=False):
        """
        Logs a user in after verifying their credentials.

        Args:
            email (str): The user's email address.
            password (str): The user's plaintext password.
            remember (bool, optional): Whether to set a "remember me" cookie.
                                       Defaults to False.

        Returns:
            dict: A standardized success or error response.
                  On success, the payload contains the user's 'profile' object.
        """
        # --- 1. Get the user from the database ---
        profile_res: dict = self.profile_manager.get_profile_by_email(email)
        is_success: bool = profile_res.get("success", False)

        # If the email was not found, return a generic error.
        # This prevents "email enumeration" attacks.
        if not is_success:
            return error_res(f"Invalid Email or Password...")

        # --- 2. Verify the password ---
        payload = profile_res.get("payload", {})
        profile: Profile = payload.get("profile")
        
        # Use the PasswordManager to securely compare the password and hash
        is_correct = self.password_manager.verify(profile.password, password)

        # If the password is not correct, return the same generic error.
        if not is_correct:
            return error_res("Invalid Email or Password...")
        
        # --- 3. Log the user in ---
        # Both email and password are correct.
        # Call Flask-Login's function to set the user in the session.
        login_user(user=profile, remember=remember)

        return success_res(payload={ "profile": profile }, msg=f"Hello {profile.first_name}!")
    
    def logout(self):
        """
        Logs the current user out.
        
        This is a simple wrapper around Flask-Login's `logout_user` function.
        """
        logout_user()

