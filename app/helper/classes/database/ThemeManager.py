"""
Manages all database operations for the Theme model.

This file defines the ThemeManager class, which is responsible for
creating, retrieving, and seeding the application's color themes.
"""

from .BaseManager import BaseManager
from app.database.models import Theme
from app.helper.functions.response_schemas import success_res, error_res
from sqlalchemy import select

class ThemeManager(BaseManager):
    """
    Handles all CRUD and query logic for color Themes.
    
    Inherits from BaseManager to get access to the session, cache,
    and generic helper methods.
    """
    
    def get_by_name(self, theme_name):
        """
        Retrieves a single theme by its unique name.

        Args:
            theme_name (str): The name of the theme to find.

        Returns:
            dict: A standardized success or error response from read_item().
        """
        return self.read_item(
            model=Theme,
            item_name="Theme",
            name=theme_name,
        )

    def get_by_id(self, theme_id):
        """
        Retrieves a single theme by its primary key.

        Args:
            theme_id (int): The ID of the theme to find.

        Returns:
            dict: A standardized success or error response from read_item().
        """
        return self.read_item(
            model=Theme,
            item_name="Theme",
            id=theme_id,
        )
    
    def create_theme(self, **theme_kwargs):
        """
        Creates a new theme in the database.

        Checks for duplicates based on theme name before creation.

        Args:
            **theme_kwargs: Keyword arguments for the new Theme model.

        Returns:
            dict: A standardized success or error response dictionary.
        """
        # Sanitize the name
        theme_kwargs["name"] = theme_kwargs.get("name", "").strip()

        # Check for duplicates
        is_duplicate = self.get_by_name(theme_kwargs["name"]).get("success")

        if is_duplicate:
            return error_res(f"Theme already created.")

        # Create the new Theme object
        theme = Theme(**theme_kwargs)

        # Use the BaseManager's create_item method
        return self.create_item(
            item=theme,
            success_msg="New theme created",
            item_name="Theme",
        )
    
    def get_default(self):
        """
        Retrieves the theme marked as the default (is_default=True).

        This is used as a fallback if a user's theme isn't found
        or during initial profile creation.

        Returns:
            dict: A standardized success or error response from read_item().
        """
        return self.read_item(
            model=Theme,
            item_name="Theme",
            is_default= True
        )
    
    def get_all(self):
        """
        Retrieves all themes from the database, ordered by name.

        This is used to populate the list of theme choices in the
        Appearance settings page.

        Returns:
            dict: A standardized success or error response dictionary.
        """
        try:
            # Build the query
            query = select(Theme).order_by(Theme.name)
            # Execute and get all results
            themes = self._session.scalars(query).all()

            if not themes:
                return error_res("Themes not found...")
            else:
                return success_res(payload={ "themes": themes }, msg="Themes found...")
        
        except Exception as e:
            return error_res(f"An error occurred retrieving themes: {e}")


    def init(self, theme_data):
        """
        Initializes the database with a list of themes from a seed file.

        This method is called by the 'flask seed-db' command. It performs
        a bulk insert of theme data.

        Args:
            theme_data (list[dict]): A list of dictionaries, where each
                                     dictionary contains the data for a new theme.

        Returns:
            dict: A standardized success or error response dictionary.
        """
        themes_to_add = []
        try:
            # Create a list of Theme objects from the provided data
            for theme in theme_data:
                new_theme = Theme(**theme)
                themes_to_add.append(new_theme)

            # Add all new themes to the session and commit at once
            self._session.add_all(themes_to_add)
            self._session.commit()

        except Exception as e:
            self._session.rollback()
            return error_res(f"Failed to create theme. Error raised: {e}")

        return success_res(payload={ "themes": themes_to_add }, msg="Themes created...")