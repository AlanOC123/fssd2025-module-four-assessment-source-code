"""
Manages all database operations for the Thought model.

This file defines the ThoughtManager class, which handles the
business logic for creating, editing, deleting, and querying thoughts.
It includes the logic for the filterable "Timeline" feature.
"""

from .BaseManager import BaseManager
from app.database.models import Thought, Profile, ProfileIdentity
from app.helper.functions.response_schemas import success_res, error_res
from flask import Flask, current_app
from sqlalchemy import select, extract, cast, Date
from datetime import datetime, timezone

class ThoughtManager(BaseManager):
    """
    Handles all CRUD and query logic for Thoughts.
    
    Inherits from BaseManager to get access to the session, cache,
    and generic helper methods.
    """
    def __init__(self, db_manager_instance) -> None:
        """
        Initializes the ThoughtManager.

        Args:
            db_manager_instance (DatabaseManager): The central DB manager.
        """
        super().__init__(db_manager_instance)
    
    def get_thought_by_id(self, thought_id) -> Thought | None:
        """
        Retrieves a single thought by its primary key.

        This is a simple, direct getter that bypasses the standardized
        response system for internal use by other manager methods.

        Args:
            thought_id (int): The primary key of the thought to retrieve.

        Returns:
            Thought | None: The SQLAlchemy Thought object if found, else None.
        """
        if not thought_id:
            return None

        # .get() is the most efficient way to query by primary key
        return self._session.get(Thought, thought_id)
    
    def create_thought(self, profile: Profile, profile_identity: ProfileIdentity, content):
        """
        Creates a new thought in the database.

        Args:
            profile (Profile): The user's Profile object.
            profile_identity (ProfileIdentity): The user's active ProfileIdentity object.
            content (str): The text content of the thought.

        Returns:
            dict: A standardized success or error response dictionary.
        """
        if not content or not profile or not profile_identity:
            return error_res("Missing core data to construct thought")

        profile_id = profile.id
        profile_identity_id = profile_identity.id

        try:
            # Create the new Thought model instance
            new_thought = Thought(
                profile_id=profile_id, 
                profile_identity_id=profile_identity_id,
                content=content
            )
            
            # Add and commit to the database
            self._session.add(new_thought)
            self._session.commit()
            return success_res(payload={}, msg="Thought created!")
        except Exception as e:
            self._session.rollback()
            return error_res(msg=f"Error creating thought. Error {e}")
    
    def get_ordered_thoughts(self, identity_id, **filter_kwargs):
        """
        Gets all thoughts for an identity, with optional time-based filtering.
        
        This method powers the "Timeline" feature.
        - If 'year' and 'month' are provided, it filters for that specific period.
        - If they are NOT provided, it defaults to filtering for "today".

        Args:
            identity_id (int): The ID of the identity to get thoughts for.
            **filter_kwargs: Optional filters, expecting 'year' and 'month'.

        Returns:
            dict: A standardized success or error response dictionary.
        """
        if not identity_id:
            return error_res("Identity not given")
        
        # Start with the base query:
        # SELECT * FROM thoughts WHERE profile_identity_id = ?
        query = select(Thought).where(
            Thought.profile_identity_id == identity_id
        )
        
        year = filter_kwargs.get("year")
        month = filter_kwargs.get("month")

        # --- This is the main filtering logic for the timeline ---
        if year and month:
            # If a year and month are provided, filter by them
            query = query.where(
                extract('year', Thought.created_at) == year,
                extract('month', Thought.created_at) == month
            )
        else:
            # If no filter is provided, default to only thoughts from today
            today = datetime.now(timezone.utc).date()
            # We must 'cast' the 'created_at' (DateTime) column to a 'Date'
            # to successfully compare it to our 'today' date object.
            query = query.where(
                cast(Thought.created_at, Date) == today
            )
        
        try:
            # Execute the final query, ordering by creation time ascending
            res = self._session.scalars(
                query.order_by(Thought.created_at.asc())
            ).all()

            return success_res(payload={ "thoughts": res }, msg="Thoughts found!")

        except Exception as e:
            return error_res(msg=f"Error getting thoughts. Error {e}")
    
    def delete_thought(self, thought_id):
        """
        Deletes a single thought from the database.

        Args:
            thought_id (int): The ID of the thought to delete.

        Returns:
            dict: A standardized success or error response dictionary.
        """
        if not thought_id:
            return error_res("Thought not given")
        
        try:
            # Use the internal getter to find the thought
            thought: Thought | None = self.get_thought_by_id(thought_id)

            if not thought:
                return error_res("Thought not found...")

            self._session.delete(thought)
            self._session.commit()
            return success_res(msg="Thought deleted!", payload={})

        except Exception as e:
            self._session.rollback()
            return error_res(msg=f"Error deleting thoughts. Error {e}")
    
    def edit_thought(self, thought_id, content):
        """
        Edits the content of a single existing thought.

        Args:
            thought_id (int): The ID of the thought to edit.
            content (str): The new text content for the thought.

        Returns:
            dict: A standardized success or error response dictionary.
        """
        if not thought_id or not content:
            return error_res("Thought not given")
    
        try:
            # Use the internal getter to find the thought
            thought = self.get_thought_by_id(thought_id)

            if not thought:
                return error_res("Thought not found...")
            
            # Update the content on the model instance
            thought.content = content

            self._session.add(thought)
            self._session.commit()
            return success_res(msg="Thought updated!", payload={})

        except Exception as e:
            self._session.rollback()
            return error_res(msg=f"Error deleting thoughts. Error {e}")

