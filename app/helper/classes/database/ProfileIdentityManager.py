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