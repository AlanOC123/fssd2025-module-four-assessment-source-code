from .BaseManager import BaseManager
from app.database.models import Theme
from app.helper.functions.response_schemas import success_res, error_res

class ThemeManager(BaseManager):
    def get_theme_by_name(self, theme_name):
        return self.read_item(
            model=Theme,
            item_name="Theme",
            name=theme_name,
        )

    def get_theme_by_id(self, theme_id):
        return self.read_item(
            model=Theme,
            item_name="Theme",
            id=theme_id,
        )
    
    def create_theme(self, **theme_kwargs):
        theme_kwargs["name"] = theme_kwargs.get("name").strip()

        # Check for duplicates
        is_duplicate = self.get_theme_by_name(theme_kwargs["name"]).get("success")

        if is_duplicate:
            return error_res(f"Theme already created.")

        theme = Theme(**theme_kwargs)

        return self.create_item(
            item=theme,
            success_msg="New theme created",
            item_name="Theme",
        )
    
    def get_default_theme(self):
        return self.read_item(
            model=Theme,
            item_name="Theme",
            is_default= True
        )