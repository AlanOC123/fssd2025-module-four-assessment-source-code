"""
Manages the ProfileIdentity model (the link between a Profile and IdentityTemplate).

This file defines the ProfileIdentityManager, which is the heart of the
"Identities" feature. It handles:
- Creating the default set of identities for new users.
- Setting, swapping, and retrieving the user's 'active' identity.
- Updating the 'custom_name' for identities.
"""

from .BaseManager import BaseManager
from app.database.models import Profile, ProfileIdentity
from app.helper.functions.response_schemas import success_res, error_res
from sqlalchemy import select

class ProfileIdentityManager(BaseManager):
    """
    Manages all database operations for the ProfileIdentity model.
    
    This class handles the link between a user's Profile and their
    chosen IdentityTemplates. It manages which identity is 'active', 
    updates custom names, and initializes the default set of identities 
    for new users.
    """
    
    def get_by_profile_id(self, profile_id) -> dict:
        """
        Gets the *first* profile identity found for a specific profile ID.

        Args:
            profile_id (int): The primary key of the user's profile.

        Returns:
            dict: A standardized response from read_item().
        """
        # Debated to use session.get but chose to utilise Base Manager to reduce error handling need
        return self.read_item(
            model=ProfileIdentity,
            item_name="Profile_Identity",
            profile_id= profile_id,
        )

    def get_by_template_id(self, template_id) -> dict:
        """
        Gets the *first* Profile Identity found that uses a specific template ID.
        
        Args:
            template_id (int): The primary key of the IdentityTemplate.

        Returns:
            dict: A standardized response from read_item().
        """
        return self.read_item(
            model=ProfileIdentity,
            item_name="Profile_Identity",
            template_id=template_id,
        )

    def create(self, **profile_identity_kwargs) -> dict:
        """
        Creates a single new link between a profile and an identity template.

        Checks for duplicates based on the composite key (profile_id, template_id)
        before creating.

        Args:
            **profile_identity_kwargs: Must include 'profile_id' and 'template_id'.

        Returns:
            dict: A standardized success or error response.
        """
        # Check for duplicates
        profile_id = profile_identity_kwargs["profile_id"]
        template_id = profile_identity_kwargs["template_id"]
        
        # Use read_item (singular) to efficiently check if *any* record
        # exists with this composite key.
        is_duplicate = self.read_item(
            model=ProfileIdentity,
            item_name="Profile_Identity", 
            profile_id=profile_id, 
            template_id=template_id).get("success"
        )

        if is_duplicate:
            return error_res(f"Profile Identity Already created.")

        # Use the BaseManager's create_item method
        return self.create_item(
            item=ProfileIdentity(**profile_identity_kwargs), 
            success_msg="Identity created", 
            item_name="Profile_Identity", 
        )
    
    def initialise_profile_identities(self, profile_id) -> dict:
        """
        Creates a list of new ProfileIdentity objects for a new user.

        This method is called during the profile registration transaction.
        It fetches all IdentityTemplates and creates a corresponding
        ProfileIdentity for each one, setting the first as 'active'.

        IMPORTANT: This method does NOT commit to the session. It only
        returns the list of objects to be added and committed by the
        calling method (e.g., ProfileManager.create_profile).

        Args:
            profile_id (int): The ID of the new profile being created.

        Returns:
            dict: A standardized response. On success, the payload contains
                    a list of new ProfileIdentity objects ('identities_list').
        """
        # Get all the templates from the IdentityTemplateManager
        template_res = self._db_manager.identity_template.get_all()

        # Verify the response is okay before continuing
        if not template_res.get("success"):
            return error_res(f"{template_res.get("msg")}")
        
        all_templates = template_res.get("payload", {}).get("identity_templates")
        
        # Add all identities to a list
        identities_to_add = []
        for template in all_templates:
            new_identity = ProfileIdentity(
                profile_id=profile_id,
                template_id=template.id,
                is_active=False
            )
            # Default the custom name to the template's name
            new_identity.custom_name = template.name
            identities_to_add.append(new_identity)
        
        # Set the first identity in the list as the default active one
        if identities_to_add:
            identities_to_add[0].is_active = True

        # Return the list but dont commit
        return success_res(payload={ "identities_list": identities_to_add }, msg="Identities successfully created...")
    
    def swap_active_identites(self, profile, current: ProfileIdentity, new: ProfileIdentity) -> dict:
        """
        Swaps the 'is_active' flag from one identity to another in one transaction.

        Args:
            profile (Profile): The user's Profile object.
            current (ProfileIdentity): The currently active identity.
            new (ProfileIdentity): The identity to make active.

        Returns:
            dict: A standardized success or error response.
        """
        if not (current and new):
            return error_res(f"Identities not given...")
        
        # If a current isn't given, check for an existing active one
        if not current:
            active_attempt = self.get_active_identity(profile).get("success")
            if active_attempt:
                current = active_attempt.get("payload", {}).get("active_identity")

        # Deactivate the old one
        if current:
            current.is_active = False

        # Activate the new one
        new.is_active = True

        try:
            # Stage both changes
            if current:
                self._session.add(current)
            self._session.add(new)
            # Commit them together
            self._session.commit()
            return success_res(payload={ "inactive": current, "active": new }, msg="Active identities set...")
        except Exception as e:
            self._session.rollback()
            return error_res(f"Error occured setting active identities")
    
    def get_active_identity(self, profile) -> dict:
        """
        Finds and returns the currently active ProfileIdentity for a user.

        Args:
            profile (Profile): The user's Profile object.

        Returns:
            dict: A standardized response. On success, the payload
                    contains the 'active_identity' object.
        """
        if not profile:
            return error_res("Missing profile...")
        
        # Filter the identities list to find the one where is_active is True
        active_list = list(filter(lambda identity: identity.is_active, profile.identities))

        if not active_list:
            # This check prevents an IndexError if no identity is active.
            return error_res("Active identity not found...")
        
        # Return the first (and only) active identity
        active_identity = active_list[0]
        return success_res(payload={ "active_identity": active_identity }, msg="Identity found...")
    
    def deactivate_identities(self, profile) -> dict:
        """
        Sets 'is_active' to False for all of a user's identities.

        This is a helper method for 'set_identity' to ensure only
        one identity can be active at a time.

        Args:
            profile (Profile): The user's Profile object.

        Returns:
            dict: A standardized success or error response.
        """
        if not profile:
            return error_res("Profile not given.")
        
        try:
            # Stage all identities to be deactivated
            for identity in profile.identities:
                identity.is_active = False
                self._session.add(identity)
            # Commit all changes in one transaction
            self._session.commit()
            return success_res(payload={}, msg="Identities deactivated.")
        except Exception as e:
            self._session.rollback()
            return error_res(f"Error deactivating identities. Error: {e}")

    def set_identity(self, profile, identity_id) -> dict:
        """
        Sets a specific identity as active for a user.

        This performs an atomic-like transaction:
        1. Calls 'deactivate_identities' (which commits).
        2. Activates the one specified by 'identity_id' (and commits).

        Args:
            profile (Profile): The user's Profile object.
            identity_id (int): The ID of the ProfileIdentity to make active.

        Returns:
            dict: A standardized success or error response.
        """
        identity: ProfileIdentity | None = self._session.get(ProfileIdentity, identity_id)

        # Return an error res if the identity wasnt found
        if not identity:
            return error_res("Identity not found.")

        # Deactivate all and set new one to active
        try:
            # --- 1. Deactivate all existing identities ---
            deactivate_res = self.deactivate_identities(profile)
            if not deactivate_res.get("success"):
                # If this fails, we can't proceed.
                return error_res(deactivate_res.get("msg", ""))

            # --- 2. Activate the new identity ---
            identity.is_active = True
            self._session.add(identity)
            self._session.commit()
            return success_res(payload={ "active_identity": identity }, msg="Identity set")
        except Exception as e:
            # Note: The 'deactivate_identities' call already committed.
            # A rollback here will only roll back the 'set_identity' part.
            # This is acceptable, as it just means no identity is active.
            self._session.rollback()
            return error_res(f"Error setting new active identity. Error: {e}")
    
    def set_default_identity(self, profile) -> dict:
        """
        Sets a default identity (the first one) as active.

        This is a fallback method, typically called on a user's first
        login or if no active identity is found (e.g., in the index route).

        Args:
            profile (Profile): The user's Profile object.

        Returns:
            dict: A standardized success or error response.
        """
        if not profile:
            return error_res("Missing profile...")
        
        # Check if one is already active before setting a default
        active_attempt = self.get_active_identity(profile)
        if active_attempt.get("success"):
            return success_res(payload=active_attempt.get("payload"), msg="Identity already set...")

        # No active identity found, set the first in the list as default
        if not profile.identities:
            return error_res(f"Profile {profile.id} has no identities to set as default.")
            
        default = profile.identities[0]
        
        try:
            default.is_active = True
            self._session.add(default)
            self._session.commit()
            return success_res(payload={ "active_identity": default }, msg="Default identity set...")
        except Exception as e:
            self._session.rollback()
            return error_res(f"Error commiting default identity. Error: {e}")

    def update_custom_names(self, profile_id, form_data) -> dict:
        """
        Updates the 'custom_name' for multiple identities from a form submission.

        This method efficiently performs a bulk update:
        1. Fetches all identities for the user.
        2. Maps them by ID for fast lookup.
        3. Loops through the submitted form data.
        4. Stages changes *only* for identities whose names have changed.
        5. Commits all changes in a single transaction.

        Args:
            profile_id (int): The user's Profile ID.
            form_data (list[dict]): The data from the 'form.identities.data'
                                    FieldList. Each dict is expected to have
                                    'identity_id' and 'identity_custom_name'.

        Returns:
            dict: A standardized response. On success, the payload
                    contains a list of 'updated' identity IDs.
        """
        try:
            # --- 1. Get all identities for this user ---
            user_identities = self._session.scalars(
                select(ProfileIdentity)
                .where(ProfileIdentity.profile_id == profile_id)
            ).all()

            # --- 2. Create a fast lookup map {id: identity_object} ---
            identity_map = { i.id: i for i in user_identities }

            # Empty array to keep track of the changed identities
            updated_ids = []

            # --- 3. Loop through the submitted form fields ---
            for item in form_data:
                # Get the id and custom name input
                identity_id = int(item["identity_id"])
                new_name = item["identity_custom_name"].strip()

                # If the ID from the form isn't in our map, skip (security)
                if identity_id not in identity_map:
                    continue
                
                # Get the identity object and its current name
                identity_to_update = identity_map[identity_id]
                curr_name = identity_to_update.custom_name or identity_to_update.template.name

                # --- 4. Compare and stage changes ---
                if new_name == curr_name:
                    # No change, do nothing
                    continue
                else:
                    # Name has changed, update it and stage for commit
                    identity_to_update.custom_name = new_name
                    updated_ids.append(identity_to_update.id)
                    self._session.add(identity_to_update)

            # --- 5. Commit all staged changes at once ---
            self._session.commit()
            return success_res(payload={ "updated": updated_ids }, msg="Identities updated successfully...")
    
        except Exception as e:
            self._session.rollback()
            return error_res(f"Error commiting identity names. Error: {e}")


