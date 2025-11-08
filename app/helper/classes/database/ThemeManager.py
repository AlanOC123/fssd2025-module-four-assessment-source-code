from .BaseManager import BaseManager
from app.database.models import Theme
from app.helper.functions.response_schemas import success_res, error_res
from sqlalchemy import select

class ThemeManager(BaseManager):
    def get_by_name(self, theme_name):
        return self.read_item(
            model=Theme,
            item_name="Theme",
            name=theme_name,
        )

    def get_by_id(self, theme_id):
        return self.read_item(
            model=Theme,
            item_name="Theme",
            id=theme_id,
        )
    
    def create_theme(self, **theme_kwargs):
        theme_kwargs["name"] = theme_kwargs.get("name", "").strip()

        # Check for duplicates
        is_duplicate = self.get_by_name(theme_kwargs["name"]).get("success")

        if is_duplicate:
            return error_res(f"Theme already created.")

        theme = Theme(**theme_kwargs)

        return self.create_item(
            item=theme,
            success_msg="New theme created",
            item_name="Theme",
        )
    
    def get_default(self):
        return self.read_item(
            model=Theme,
            item_name="Theme",
            is_default= True
        )
    
    def get_all(self):
        query = select(Theme).order_by(Theme.name)
        themes = self._session.scalars(query).all()

        if not themes:
            return error_res("Themes not found...")
        
        else:
            return success_res(payload={ "themes": themes }, msg="Themes found...")


    def init(self, theme_data):
        # Empty list to add identities too
        themes_to_add = []
        try:
            # Create and add a theme
            for theme in theme_data:
                new_theme = Theme(**theme)
                themes_to_add.append(new_theme)

            # Try commit them all together
            self._session.add_all(themes_to_add)
            self._session.commit()

        except Exception as e:
            self._session.rollback()
            return error_res(f"Failed to create theme. Error raised: {e}")

        return success_res(payload={ "themes": themes_to_add }, msg="Themes created...")