from .BaseManager import BaseManager
from app.database.models import IdentityTemplate
from app.helper.functions.response_schemas import success_res, error_res

class IdentityTemplateManager(BaseManager):
    def get_by_name(self, identity_name):
        return self.read_item(
            model=IdentityTemplate,
            item_name="IdentityTemplate",
            name=identity_name
        )
    
    def get_all(self):
        return self.read_items(
            model=IdentityTemplate,
            item_name="Identity",
        )

    def create(self, **identity_kwargs):
        identity_kwargs["name"] = identity_kwargs.get("name").strip()
        
        # Check for duplicates
        is_duplicate = self.get_by_name(identity_kwargs["name"]).get("success")

        if is_duplicate:
            return error_res(f"Identity already created.")

        return self.create_item(
            item=IdentityTemplate(**identity_kwargs), 
            success_msg="Identity created", 
            item_name="Identity", 
        )