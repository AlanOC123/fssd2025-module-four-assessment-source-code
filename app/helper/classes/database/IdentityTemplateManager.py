from .BaseManager import BaseManager
from app.database.models import IdentityTemplate
from app.helper.functions.response_schemas import success_res, error_res
from sqlalchemy.exc import IntegrityError

class IdentityTemplateManager(BaseManager):
    def get_by_name(self, identity_name):
        return self.read_item(
            model=IdentityTemplate,
            item_name="Identity_Template",
            name=identity_name
        )
    
    def get_all(self):
        return self.read_items(
            model=IdentityTemplate,
            item_name="Identity_Templates",
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
            item_name="Identity_Template", 
        )
    
    def init(self, template_data):
        # Empty list to add Templates too
        templates_to_add = []
        try:
            # Iterate over the templates
            for template in template_data:
                # Create and add a template
                new_template = IdentityTemplate(**template)
                templates_to_add.append(new_template)

            # Try commit the Teamplates to the DB
            self._session.add_all(templates_to_add)
            self._session.commit()

        except Exception as e:
            self._session.rollback()
            return error_res(f"Failed to create template. Error raised: {e}")

        return success_res(payload={ "templates": templates_to_add }, msg="Templates created...")