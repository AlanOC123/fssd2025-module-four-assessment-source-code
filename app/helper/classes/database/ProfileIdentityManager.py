from .BaseManager import BaseManager
from app.database.models import ProfileIdentity
from app.helper.functions.response_schemas import success_res, error_res

class ProfileIdentityManager(BaseManager):
    def get_by_profile_id(self, profile_id):
        return self.read_item(
            model=ProfileIdentity,
            item_name="Profile_Identity",
            profile_id= profile_id,
        )

    def get_by_template_id(self, template_id):
        return self.read_item(
            model=ProfileIdentity,
            item_name="Profile_Identity",
            template_id=template_id,
        )

    def create(self, **profile_identity_kwargs):        
        # Check for duplicates
        profile_id = profile_identity_kwargs["profile_id"]
        template_id = profile_identity_kwargs["template_id"]
        is_duplicate = self.read_item(
            model=ProfileIdentity,
            item_name="Profile_Identity", 
            profile_id=profile_id, 
            template_id=template_id).get("success"
        )

        if is_duplicate:
            return error_res(f"Profile Identity Already created.")

        return self.create_item(
            item=ProfileIdentity(**profile_identity_kwargs), 
            success_msg="Identity created", 
            item_name="Profile_Identity", 
        )
    
    def initialise_profile_identities(self, profile_id):
        # Get all the templates
        template_res = self._db_manager.identity_template.get_all()
        print(template_res)

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
            identities_to_add.append(new_identity)
        
        # Set the first as the default
        identities_to_add[0].is_active = True

        # Return the list but dont commit
        return success_res(payload={ "identities_list": identities_to_add }, msg="Identities successfully created...")
    
    def swap_active_identites(self, profile, current: ProfileIdentity, new: ProfileIdentity):
        if not (current and new):
            return error_res(f"Identities not given...")
        
        if not current:
            active_attempt = self.get_active_identity(profile).get("success")
            if active_attempt:
                current = active_attempt.get("payload", {}).get("active_identity")

        if current:
            current.is_active = False

        new.is_active = True

        try:
            if current:
                self._session.add(current)
            self._session.add(new)
            self._session.commit()
            return success_res(payload={ "inactive": current, "active": new }, msg="Active identities set...")
        except Exception as e:
            self._session.rollback()
            return error_res(f"Error occured setting active identities")
    
    def get_active_identity(self, profile):
        if not profile:
            return error_res("Missing profile...")
        
        active_identity = list(filter(lambda identity: identity.is_active ,profile.identities))[0]

        if not active_identity:
            return error_res("Active identity not found...")
        
        return success_res(payload={ "active_identity": active_identity }, msg="Identity found...")
    
    def deactivate_identities(self, profile):
        if not profile:
            return error_res("Profile not given.")
        
        try:
            for identity in profile.identities:
                identity.is_active = False
                self._session.add(identity)
            self._session.commit()
            return success_res(payload={}, msg="Identities deactivated.")
        except Exception as e:
            self._session.rollback()
            return error_res(f"Error deactivating identities. Error: {e}")

    
    def set_identity(self, profile, identity):
        if not identity:
            return error_res("Identity not given.")

        try:
            deactivate_res = self.deactivate_identities(profile)
            if not deactivate_res.get("success"):
                return error_res(deactivate_res.get("msg", ""))

            identity.is_active = True
            self._session.add(identity)
            self._session.commit()
            return success_res(payload={ "active_identity": identity }, msg="Identity set")
        except Exception as e:
            return error_res(f"Error deactivating identities. Error: {e}")
    
    def set_default_identity(self, profile):
        if not profile:
            return error_res("Missing profile...")
        
        active_attempt = self.get_active_identity(profile)

        if active_attempt.get("success"):
            return success_res(payload=active_attempt.get("payload"), msg="Identity already set...")

        default = profile.identities[0]
        
        try:
            default.is_active = True
            self._session.add(default)
            self._session.commit()
            return success_res(payload={ "active_identity": default }, msg="Default identity set...")
        except Exception as e:
            self._session.rollback()
            return error_res(f"Error commiting default identity. Error: {e}")


