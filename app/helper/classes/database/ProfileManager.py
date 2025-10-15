from .BaseManager import BaseManager
from app.database.models import Profile
import os
import bcrypt
from app.helper.functions.response_schemas import success_res, error_res
from string import punctuation
from datetime import datetime

class ProfileManager(BaseManager):
    _min_pw_len = 8

    def check_password(self, profile: Profile, password: str) -> bool:
        password = password.strip()
        # Match password types to byters
        password_bytes = password.encode('utf-8')
        hashed_pw = profile.password.encode('utf-8')

        # Return if they match
        matches = bcrypt.checkpw(hashed_password=hashed_pw, password=password_bytes)
        return matches

    # Returns a hashed password to submit to the db
    def hash_password(self, password: str) -> bytes:
        bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hash = bcrypt.hashpw(bytes, salt)
        return hash

    # Validates the password constraints
    def validate_password(self, password: str) -> tuple:
        length_ok = len(password) >= self._min_pw_len
        has_special = any(c in punctuation for c in password)
        has_cap = any(c.isupper() for c in password)

        if not length_ok:
            return (False, "Password too short")
        
        if not has_special:
            return (False, "Password must contain a special character like $, @ or !")

        if not has_cap:
            return (False, "Password must contain a capital letter")

        return (True, "Password meets requirements")

    # Retreives a profile from the DB
    def get_profile_by_email(self, email: str) -> dict:
        return self.read_item(
            model=Profile,
            item_name="Profile",
            email= email,
        )

    # Retrives a profile using an id
    def get_profile_by_id(self, id: int) -> dict:
        return self.read_item(
            model=Profile,
            item_name="Profile",
            id=id,
        )
    
    # Create a new profile
    def create_profile(self, **profile_kwargs) -> dict:
        password = profile_kwargs.get("password").strip()

        dob = profile_kwargs["date_of_birth"]

        if dob:
            dob = datetime.strptime(dob, '%Y-%m-%d').date()
        
        profile_kwargs["date_of_birth"] = dob

        # Check password strength
        valid_password, password_msg = self.validate_password(password)

        if not valid_password:
            return error_res(password_msg)
        
        # Check for duplicates
        is_duplicate = self.get_profile_by_email(profile_kwargs["email"]).get("success")

        if is_duplicate:
            return error_res(f"User already registered. Sign in?")

        # Hash password before committing
        profile_kwargs["password"] = self.hash_password(password).decode('utf-8')

        identities = self._db_manager.identity_template.get_all()

        theme_res = self._db_manager.theme.get_default_theme()

        if not theme_res.get("success"):
            return error_res(f"Integrity error. Failed to get default theme {theme_res.get("msg")}")
        
        profile_kwargs["theme_id"] = theme_res.get("payload").get("theme").id

        res = self.create_item(
            item=Profile(**profile_kwargs), 
            success_msg="Profile created", 
            item_name="Profile", 
        )

        profile = res.get("payload").get("profile")

        profile_identities = []

        for template in identities.get("payload").get("identity"):
            profile_identity_raw = {
                "template_id": template.id,
                "profile_id": profile.id
            }
            identity_res = self._db_manager.profile_identity.create(**profile_identity_raw)

            profile_identities.append(identity_res.get("payload").get("profile_identity"))

        return res