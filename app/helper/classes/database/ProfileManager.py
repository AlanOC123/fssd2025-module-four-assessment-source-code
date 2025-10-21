from .BaseManager import BaseManager
from app.database.models import Profile
from bcrypt import checkpw, hashpw, gensalt
from app.helper.functions.response_schemas import success_res, error_res
from string import punctuation
from datetime import datetime
from flask import Flask, current_app

class PasswordManager:
    _CONFIG: dict = {}

    def __init__(self, config) -> None:
        self._CONFIG: dict = config

    def check_len(self, password: str) -> bool:
        pw_len: int = len(password.strip())
        min_len: int = self._CONFIG.get("PASSWORD_MIN_LENGTH", 8)
        max_len: int = self._CONFIG.get("PASSWORD_MAX_LENGTH", 128)
        return pw_len >= min_len and pw_len <= max_len

    def check_cap(self, password: str) -> bool:
        needs_cap: bool = self._CONFIG.get("PASSWORD_CONTAINS_CAP", True)
        return True if not needs_cap else any(c.isupper() for c in password)
    
    def check_complexity(self, password: str):
        needs_symbol = self._CONFIG.get("PASSWORD_CONTAINS_SYMBOL", True)
        return True if not needs_symbol else any(c in punctuation for c in password)

    def verify(self, pw_challenge_hash: str, pw_attempt_string: str) -> bool:
        if not (isinstance(pw_challenge_hash, str) and isinstance(pw_attempt_string, str)):
            return False
        return checkpw(pw_attempt_string.strip().encode('utf-8'), pw_challenge_hash.strip().encode('utf-8'))
    
    def hashpw(self, password: str) -> bytes:
        return hashpw(password.strip().encode('utf-8'), gensalt())
    
    @property
    def min_pw_length(self):
        return self._CONFIG.get("PASSWORD_MIN_LENGTH", 8)
    
    @property
    def max_pw_length(self):
        return self._CONFIG.get("PASSWORD_MAX_LENGTH", 128)
    
class ProfileValidator:
    def validate_name(self, first_name, surname):
        return first_name and isinstance(first_name, str) and surname and isinstance(surname, str)
    
    def validate_email(self, email_str):
        return email_str and isinstance(email_str, str) and '@' in email_str
    
    def validate_dob(self, dob_str):
        return 


class ProfileManager(BaseManager):
    def __init__(self, db_manager_instance, pw_manager) -> None:
        super().__init__(db_manager_instance)
        self.pw_manager: PasswordManager = pw_manager

    def _validate_and_extract_data(self, **profile_data):
        # Extract Core Data and Basic Sanitisation
        first_name = profile_data.get("first_name", "").strip()
        surname = profile_data.get("surname", "").strip()
        dob_str = profile_data.get("date_of_birth", "").strip()
        email = profile_data.get("email", "").strip()
        password = profile_data.get("password", "")

        # Validate Data Presence and Format
        if not first_name: return error_res(f"First Name is required...")
        if not surname: return error_res(f"Surname is required...")
        if not dob_str: return error_res(f"Date of Birth is required...")
        if not email: return error_res(f"Email is required...")
        if not password: return error_res(f"Password is required...")

        # Validate Email
        if not '@' in email:
            return error_res(f"Invalid Email. Doesnt contain @. Email: {email}")
        
        # Check for Duplicate Profile
        if self.get_profile_by_email(email).get("success"):
            return error_res("Data integrity issue raised during creation process.")

        # Validate Date Format
        try:
            datetime.strptime(dob_str, "%Y-%m-%d").date()
        except ValueError as e:
            return error_res(f"Error parsing date. Ensure it is in the format YYYY-MM-DD. Date: {dob_str}")

        # Validate Password
        if not self.pw_manager.check_len(password): 
            return error_res(f"Password must be between {self.pw_manager.min_pw_length} and {self.pw_manager.max_pw_length} characters in length.")
        if not self.pw_manager.check_cap(password): return error_res(f"Password must contain a capital letter.")
        if not self.pw_manager.check_complexity(password): 
            return error_res(f"Password must contain a symbol like @, !, $, etc.")

        # Transform Data
        try:
            # Submit Required Data and Preserve Optional
            sanitised_data = {
                "first_name": first_name.capitalize(),
                "surname": surname,
                "date_of_birth": datetime.strptime(dob_str, "%Y-%m-%d").date(),
                "email" : email,
                "password": self.pw_manager.hashpw(password.strip()).decode("utf-8"),
            }

            optional_fields = ["theme_name", "stay_logged_in"]
            for key in optional_fields:
                if key in profile_data:
                    sanitised_data[key] = profile_data[key]

            return success_res(payload={ "sanitised_data": sanitised_data }, msg="Data prepared successfully...")

        except Exception as e:
            return error_res(f"Error raised during transformation process: {e}")

    # Retreives a profile from the DB
    def get_profile_by_email(self, email: str) -> dict:
        return self.read_item(
            model=Profile,
            item_name="Profile",
            email=email,
        )

    # Retrives a profile using an id
    def get_profile_by_id(self, id: int) -> dict:
        return self.read_item(
            model=Profile,
            item_name="Profile",
            id=id,
        )

    # Create a new profile
    def create_profile(self, **profile_data) -> dict:
        # Validate and Sanitise Data
        data_prep_res = self._validate_and_extract_data(**profile_data)

        # Check process completed
        is_valid = data_prep_res.get("success")
        if not is_valid:
            return error_res(f"{data_prep_res.get("msg")}")

        # Get the sanitised data and create a profile
        sanitised_data = data_prep_res.get("payload", {}).get("sanitised_data", {})

        # Try to Add a new Profile
        try:
            # --Transaction Start--

            # Get The Theme ID
            theme_name = sanitised_data.get("theme_name", "Default")
            theme_res = self._db_manager.theme.get_by_name(theme_name)

            # Check for failure
            if not theme_res.get("success"):
                return error_res(f"Failed to load Theme. Required for Profile creation integrity...")

            # Redefining the theme to be referenced by ID for the Table Schema
            theme_id = theme_res.get("payload", {}).get("theme").id
            sanitised_data["theme_id"] = theme_id
            sanitised_data.pop("theme_name")

            # Create the profile and add it
            new_profile = Profile(**sanitised_data)
            self._session.add(new_profile)

            # Flush to get the ID of the profile
            self._session.flush()

            # Create the identities using the ID
            created_identities_res = self._db_manager.profile_identity.initialise_profile_identities(new_profile.id)
            is_valid_identities_list = created_identities_res.get("success")

            # Check for valid response
            if not is_valid_identities_list:
                return error_res(f"{created_identities_res.get("msg")}")
            
            # Add identities to the session
            identities_list = created_identities_res.get("payload", {}).get("identities_list", [])
            self._session.add_all(identities_list)

            # Commit the changes
            self._session.commit()
            return success_res(payload={ "profile": new_profile }, msg="Profile created...")

        except Exception as e:
            self._session.rollback()
            return error_res(f"Error creating profile. Error Raised: {e}")
    
    def _validate_and_sanitise_sign_in(self, **sign_in_data):
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

            optional_keys = ["stay_logged_in"]

            for key in optional_keys:
                if key not in sanitised_data:
                    sanitised_data[key] = sign_in_data.get(key)

            return success_res(payload={ "sanitised_data": sanitised_data }, msg="Sign in data sanitised...")

        except Exception as e:
            return error_res(f"Something went wrong signing in. Error: {e}")

    def check_sign_in(self, **sign_in_data):
        # Get and validate data
        data_prep_res = self._validate_and_sanitise_sign_in(**sign_in_data)
        is_valid = data_prep_res.get("success")

        # Break early if its not valid
        if not is_valid:
            return error_res(f"{data_prep_res.get("msg")}")
        
        sanitised_data = data_prep_res.get("payload", {}).get("sanitised_data", {})

        # Query the DB for the email
        db_res = self.get_profile_by_email(sanitised_data.get("email", ""))

        # If not successful break early with a vague error
        if not db_res.get("success"):
            return error_res(f"Invalid Email or Password")
        
        # Get the profile and check the password
        profile: Profile = db_res.get("payload", {}).get("profile")
        if not self.pw_manager.verify(profile.password, sanitised_data.get("password", "")):
            return error_res("Invalid Email or Password")

        # Return a successful login
        return success_res(payload={ "profile_id": profile.id }, msg="Sign in successful...")