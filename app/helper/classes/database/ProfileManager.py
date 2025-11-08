"""
Manages profile, user authentication, and password-related logic.

This file defines three classes:
- PasswordManager: Handles password hashing, verification, and complexity rules.
- ProfileValidator: A (currently incomplete) helper for validating profile data.
- ProfileManager: The main class for all Profile model database operations,
  including registration, sign-in, updates, and deletion.
"""

from .BaseManager import BaseManager
from app.database.models import Profile
from bcrypt import checkpw, hashpw, gensalt
from app.helper.functions.response_schemas import success_res, error_res
from string import punctuation
from datetime import datetime
from flask import Flask, current_app

class PasswordManager:
    """
    Handles all password-related logic based on app configuration.
    
    This class reads password complexity rules (length, caps, symbols)
    from the Flask app config and provides methods to hash, verify,
    and check passwords against those rules.
    """
    _CONFIG: dict = {}

    def __init__(self, config) -> None:
        """
        Initializes the PasswordManager.

        Args:
            config (dict): The Flask app config dictionary.
        """
        self._CONFIG: dict = config

    def check_len(self, password: str) -> bool:
        """
        Checks if a password meets the configured length requirements.

        Args:
            password (str): The plaintext password to check.

        Returns:
            bool: True if the password length is valid, False otherwise.
        """
        pw_len: int = len(password.strip())
        min_len: int = self._CONFIG.get("PASSWORD_MIN_LENGTH", 8)
        max_len: int = self._CONFIG.get("PASSWORD_MAX_LENGTH", 128)
        return pw_len >= min_len and pw_len <= max_len

    def check_cap(self, password: str) -> bool:
        """
        Checks if a password contains a capital letter, if required by config.

        Args:
            password (str): The plaintext password to check.

        Returns:
            bool: True if the password meets the capital letter requirement, 
                  False otherwise.
        """
        needs_cap: bool = self._CONFIG.get("PASSWORD_CONTAINS_CAP", True)
        # If the rule is disabled, always return True.
        # Otherwise, check if any character in the password is uppercase.
        return True if not needs_cap else any(c.isupper() for c in password)
    
    def check_complexity(self, password: str):
        """
        Checks if a password contains a symbol, if required by config.

        Args:
            password (str): The plaintext password to check.

        Returns:
            bool: True if the password meets the symbol requirement, 
                  False otherwise.
        """
        needs_symbol = self._CONFIG.get("PASSWORD_CONTAINS_SYMBOL", True)
        # If the rule is disabled, always return True.
        # Otherwise, check if any character is in the 'punctuation' string.
        return True if not needs_symbol else any(c in punctuation for c in password)

    def verify(self, pw_challenge_hash: str, pw_attempt_string: str) -> bool:
        """
        Verifies a plaintext password attempt against a stored bcrypt hash.

        Args:
            pw_challenge_hash (str): The stored bcrypt hash from the database.
            pw_attempt_string (str): The plaintext password from the user.

        Returns:
            bool: True if the password matches the hash, False otherwise.
        """
        if not (isinstance(pw_challenge_hash, str) and isinstance(pw_attempt_string, str)):
            return False
        
        # Use bcrypt's checkpw to securely compare the password and hash
        return checkpw(pw_attempt_string.strip().encode('utf-8'), pw_challenge_hash.strip().encode('utf-8'))
    
    def hashpw(self, password: str) -> bytes:
        """
        Hashes a plaintext password using bcrypt.

        Args:
            password (str): The plaintext password to hash.

        Returns:
            bytes: The resulting bcrypt hash as bytes.
        """
        return hashpw(password.strip().encode('utf-8'), gensalt())
    
    @property
    def min_pw_length(self):
        """Property to expose the min password length from config."""
        return self._CONFIG.get("PASSWORD_MIN_LENGTH", 8)
    
    @property
    def max_pw_length(self):
        """Property to expose the max password length from config."""
        return self._CONFIG.get("PASSWORD_MAX_LENGTH", 128)
    
class ProfileValidator:
    """
    A helper class for validating profile fields.
    NOTE: This class appears to be incomplete and not fully utilized.
    """
    def validate_name(self, first_name, surname):
        """Validates first name and surname."""
        return first_name and isinstance(first_name, str) and surname and isinstance(surname, str)
    
    def validate_email(self, email_str):
        """Validates email format."""
        return email_str and isinstance(email_str, str) and '@' in email_str
    
    def validate_dob(self, dob_str):
        """Placeholder for DOB validation."""
        return 


class ProfileManager(BaseManager):
    """
    Manages all database operations related to the Profile model.

    This includes user registration (create_profile), login (check_sign_in),
    and profile updates (update_profile, change_password, delete_account).
    It uses the PasswordManager for all password-related tasks.
    """
    def __init__(self, db_manager_instance, pw_manager) -> None:
        """
        Initializes the ProfileManager.

        Args:
            db_manager_instance (DatabaseManager): The central DB manager.
            pw_manager (PasswordManager): An instance of the PasswordManager.
        """
        super().__init__(db_manager_instance)
        self.pw_manager: PasswordManager = pw_manager

    def _validate_and_extract_data(self, **profile_data):
        """
        Private helper to validate and sanitize data for a new profile.

        This is used *only* by the create_profile method. It checks for
        presence, format, duplicates, and password complexity.

        Args:
            **profile_data: Keyword arguments from the registration form.

        Returns:
            dict: A standardized response. On success, the payload contains
                  a dictionary named 'sanitised_data'.
        """
        # --- 1. Extract Core Data and Basic Sanitisation ---
        first_name = profile_data.get("first_name", "").strip()
        surname = profile_data.get("surname", "").strip()
        dob_str = profile_data.get("date_of_birth", "")
        if isinstance(dob_str, str):
            dob_str = dob_str.strip()
        email = profile_data.get("email", "").strip()
        password = profile_data.get("password", "")

        # --- 2. Validate Data Presence ---
        if not first_name: return error_res(f"First Name is required...")
        if not surname: return error_res(f"Surname is required...")
        if not dob_str: return error_res(f"Date of Birth is required...")
        if not email: return error_res(f"Email is required...")
        if not password: return error_res(f"Password is required...")

        # --- 3. Validate Data Format & Rules ---
        # Validate Email
        if not '@' in email:
            return error_res(f"Invalid Email. Doesnt contain @. Email: {email}")
        
        # Check for Duplicate Profile by querying the database
        if self.get_profile_by_email(email).get("success"):
            return error_res("Data integrity issue raised during creation process.")

        # Validate Date Format
        try:
            if isinstance(dob_str, str):
                datetime.strptime(dob_str, "%Y-%m-%d").date()
        except ValueError as e:
            return error_res(f"Error parsing date. Ensure it is in the format YYYY-MM-DD. Date: {dob_str}")

        # Validate Password using PasswordManager
        if not self.pw_manager.check_len(password): 
            return error_res(f"Password must be between {self.pw_manager.min_pw_length} and {self.pw_manager.max_pw_length} characters in length.")
        if not self.pw_manager.check_cap(password): 
            return error_res(f"Password must contain a capital letter.")
        if not self.pw_manager.check_complexity(password): 
            return error_res(f"Password must contain a symbol like @, !, $, etc.")

        # --- 4. Transform Data ---
        try:
            # Re-check date format after validation (redundant but safe)
            if isinstance(dob_str, str):
                try:
                    datetime.strptime(dob_str, "%Y-%m-%d").date()
                except ValueError as e:
                    return error_res(f"Error parsing date. Ensure it is in the format YYYY-MM-DD. Date: {dob_str}")

            # Build the final sanitized dictionary
            sanitised_data = {
                "first_name": first_name.capitalize(),
                "surname": surname,
                "date_of_birth": dob_str,
                "email" : email,
                "password": self.pw_manager.hashpw(password.strip()).decode("utf-8"),
            }

            # Add optional fields if they were provided
            optional_fields = ["theme_name", "stay_logged_in"]
            for key in optional_fields:
                if key in profile_data:
                    sanitised_data[key] = profile_data[key]

            return success_res(payload={ "sanitised_data": sanitised_data }, msg="Data prepared successfully...")

        except Exception as e:
            return error_res(f"Error raised during transformation process: {e}")

    def get_profile_by_email(self, email: str) -> dict:
        """
        Retrieves a single profile from the DB using their email address.

        Args:
            email (str): The email address to query.

        Returns:
            dict: A standardized response from read_item().
        """
        return self.read_item(
            model=Profile,
            item_name="Profile",
            email=email,
        )

    def get_profile_by_id(self, id: int) -> dict:
        """
        Retrieves a single profile from the DB using their primary key ID.
        Used by Flask-Login's user_loader.

        Args:
            id (int): The profile's primary key.

        Returns:
            dict: A standardized response from read_item().
        """
        return self.read_item(
            model=Profile,
            item_name="Profile",
            id=id,
        )

    def create_profile(self, **profile_data) -> dict:
        """
        Creates a new user profile, hashes their password, and initializes
        their default identities. This is an atomic transaction.

        Args:
            **profile_data: Keyword arguments from the registration form.

        Returns:
            dict: A standardized success or error response.
        """
        # --- 1. Validate and sanitize all incoming data ---
        data_prep_res = self._validate_and_extract_data(**profile_data)
        is_valid = data_prep_res.get("success")
        if not is_valid:
            # Validation failed, return the specific error message
            return error_res(f"{data_prep_res.get("msg")}")

        # Get the clean, hashed data
        sanitised_data = data_prep_res.get("payload", {}).get("sanitised_data", {})

        # --- 2. Begin Atomic Database Transaction ---
        try:
            # --Transaction Start--

            # Get the Theme ID from the theme_name
            theme_name = sanitised_data.get("theme_name", "Default")
            theme_res = self._db_manager.theme.get_by_name(theme_name)

            # Fallback to the default theme if the specified one isn't found
            if not theme_res.get("success"):
                theme_res = self._db_manager.theme.get_default()

            # Get the theme's primary key ID
            theme_id = theme_res.get("payload", {}).get("theme").id
            
            # Update sanitised_data to use theme_id (required by DB model)
            sanitised_data["theme_id"] = theme_id
            sanitised_data.pop("theme_name") # Remove the temporary name

            # Create the Profile model instance
            new_profile = Profile(**sanitised_data)
            self._session.add(new_profile)

            # Flush the session to get the new_profile.id from the DB
            self._session.flush()

            # --- 3. Initialize Default Identities ---
            # Use the new profile ID to create the default identities
            created_identities_res = self._db_manager.profile_identity.initialise_profile_identities(new_profile.id)
            if not created_identities_res.get("success"):
                # If identity creation fails, roll back the whole transaction
                return error_res(f"{created_identities_res.get("msg")}")
            
            # Add the new identities to the session
            identities_list = created_identities_res.get("payload", {}).get("identities_list", [])
            self._session.add_all(identities_list)

            # --- 4. Commit Transaction ---
            # Commit both the new Profile and the new ProfileIdentities
            self._session.commit()
            return success_res(payload={ "profile": new_profile }, msg="Profile created...")

        except Exception as e:
            # If any part fails, roll back everything to maintain data integrity
            self._session.rollback()
            return error_res(f"Error creating profile. Error Raised: {e}")
    
    def _validate_and_sanitise_sign_in(self, **sign_in_data):
        """
        Private helper to validate and sanitize data for a login attempt.

        Args:
            **sign_in_data: Keyword arguments from the login form (email, password).

        Returns:
            dict: A standardized response. On success, the payload contains
                  a dictionary named 'sanitised_data'.
        """
        # Extract Data and Basic Sanitisation
        email = sign_in_data.get("email", "").strip()
        password = sign_in_data.get("password", "")

        # Validate Data Exists
        if not email or not password:
            return error_res(f"Missing Email or Password.")

        # Validate Core Shape
        if not '@' in email:
            return error_res(f"Invalid Email. {email}")

        # Return a clean copy
        try:
            sanitised_data = {
                "email": email,
                "password": password.strip()
            }

            # Preserve optional fields like 'stay_logged_in'
            optional_keys = ["stay_logged_in"]
            for key in optional_keys:
                if key not in sanitised_data:
                    sanitised_data[key] = sign_in_data.get(key)

            return success_res(payload={ "sanitised_data": sanitised_data }, msg="Sign in data sanitised...")

        except Exception as e:
            return error_res(f"Something went wrong signing in. Error: {e}")

    def check_sign_in(self, **sign_in_data):
        """
        Verifies a user's email and password for a login attempt.

        Args:
            **sign_in_data: Keyword arguments from the login form.

        Returns:
            dict: A standardized response. On success, the payload contains
                  the user's 'profile_id'.
        """
        # --- 1. Validate and sanitize incoming data ---
        data_prep_res = self._validate_and_sanitise_sign_in(**sign_in_data)
        is_valid = data_prep_res.get("success")
        if not is_valid:
            return error_res(f"{data_prep_res.get("msg")}")
        
        sanitised_data = data_prep_res.get("payload", {}).get("sanitised_data", {})

        # --- 2. Find the user in the database ---
        db_res = self.get_profile_by_email(sanitised_data.get("email", ""))
        if not db_res.get("success"):
            # Vague error for security. We don't want to confirm if the
            # email exists or not (timing attacks aside).
            return error_res(f"Invalid Email or Password")
        
        # --- 3. Verify the password ---
        profile: Profile = db_res.get("payload", {}).get("profile")
        if not self.pw_manager.verify(profile.password, sanitised_data.get("password", "")):
            # Vague error for security.
            return error_res("Invalid Email or Password")

        # --- 4. Success ---
        return success_res(payload={ "profile_id": profile.id }, msg="Sign in successful...")
    
    def update_profile(self, profile,  **profile_data):
        """
        Updates an existing profile with new data.

        This is a generic update method. It iterates over keyword arguments
        and sets them on the model instance if the attribute exists.

        Args:
            profile (Profile): The SQLAlchemy Profile model instance to update.
            **profile_data: Keyword arguments of fields to update 
                                (e.g., first_name="John").

        Returns:
            dict: A standardized success or error response.
        """
        if not profile:
            return error_res("No profile given.")
        
        # Iterate over all provided data
        for key, value in profile_data.items():
            # Check if the Profile model has this attribute
            if hasattr(profile, key):
                # Update the attribute on the model instance
                setattr(profile, key, value)
        
        try:
            # Add the modified instance to the session and commit
            self._session.add(profile)
            self._session.commit()
            return success_res(payload={}, msg="Settings saved!")
        except Exception as e:
            self._session.rollback()
            return error_res(f"Error updating profile. Error: {e}")
        
    def change_password(self, profile, new_password):
        """
        Updates a user's password after validating the new password.

        Args:
            profile (Profile): The SQLAlchemy Profile model instance to update.
            new_password (str): The new plaintext password.

        Returns:
            dict: A standardized success or error response.
        """
        if not profile:
            return error_res("No profile given.")
        
        if not new_password:
            return error_res("No password given.")

        # --- 1. Validate new password complexity ---
        if not self.pw_manager.check_len(new_password): 
            return error_res(f"Password must be between {self.pw_manager.min_pw_length} and {self.pw_manager.max_pw_length} characters in length.")
        if not self.pw_manager.check_cap(new_password): 
            return error_res(f"Password must contain a capital letter.")
        if not self.pw_manager.check_complexity(new_password): 
            return error_res(f"Password must contain a symbol like @, !, $, etc.")

        # --- 2. Hash and update password ---
        try:
            profile.password = self.pw_manager.hashpw(new_password).decode('utf-8')
            self._session.add(profile)
            self._session.commit()
            return success_res(payload={}, msg="Password updated!")

        except Exception as e:
            self._session.rollback()
            return error_res(f"Error updating profile. Error: {e}")
        
    def delete_account(self, profile):
        """
        Permanently deletes a user's account and all associated data.

        Note: Associated data (projects, tasks, etc.) is deleted via
        'cascade="all, delete-orphan"' set on the Profile model relationships.

        Args:
            profile (Profile): The SQLAlchemy Profile model instance to delete.

        Returns:
            dict: A standardized success or error response.
        """
        if not profile:
            return error_res("No profile given.")

        try:
            # Store email to verify deletion after commit
            email = profile.email
            
            # --- 1. Delete from session ---
            self._session.delete(profile)
            self._session.commit()

            # --- 2. Verify deletion ---
            check_res = self.get_profile_by_email(email)
            account_still_exists = check_res.get("success")

            if account_still_exists:
                # This should not happen. Raise an error to force a rollback.
                raise ValueError("Account still exists after deletion attempt!")

            return success_res(payload={}, msg="Profile successfully deleted.")

        except Exception as e:
            self._session.rollback()
            return error_res(f"Error deleting profile. Error: {e}")