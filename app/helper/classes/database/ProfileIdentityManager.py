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