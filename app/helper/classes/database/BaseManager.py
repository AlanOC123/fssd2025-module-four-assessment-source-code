"""
Defines the BaseManager class, the parent for all database manager classes.

This file provides the core reusable logic for common database operations,
including caching, session management, and generic CRUD (Create, Read,
Update, Delete) methods that are inherited by specific managers
(e.g., ProfileManager, ProjectManager).
"""

from flask import Flask, g
from app import get_db
from sqlalchemy import select, insert, update, delete
from app.helper.functions.response_schemas import success_res, error_res
from sqlalchemy.exc import IntegrityError

class BaseManager():
    """
    Provides core CRUD operations and session management for child managers.

    This class is not intended to be used directly, but rather inherited by
    specific data model managers (e.g., ProfileManager, ProjectManager).
    It handles database session access, request-level caching,
    and standardized success/error response generation for database operations.
    """
    def __init__(self, db_manager_instance) -> None:
        """
        Initializes the BaseManager.

        Args:
            db_manager_instance (DatabaseManager): An instance of the main
                                                  DatabaseManager to allow
                                                  access to other managers.
        """
        from app.helper.classes.database.DatabaseManager import DatabaseManager
        self._db_manager: DatabaseManager = db_manager_instance
    
    @property
    def _session(self):
        """
        Provides safe access to the database session for the current request.

        Uses the Flask 'g' object to store the session, ensuring it is created
        once per request and is available to all manager methods.

        Returns:
            sqlalchemy.orm.Session: The database session for this request.
        """
        if not "db_session" in g:
            # Get the db object from the app and create a new session
            db_object = get_db()
            g.db_session = db_object.session

        return g.db_session

    @property
    def _cache(self):
        """
        Provides a simple, request-level dictionary for caching results.

        Uses the Flask 'g' object to store a cache dictionary, which persists
        for the life of a single request. This prevents duplicate database
        queries within the same request.

        Returns:
            dict: A dictionary to be used for caching query results.
        """
        if "request_cache" not in g:
            # Initialize an empty cache if one doesn't exist for this request
            g.request_cache = {}
        
        return g.request_cache
    
    def read_item(self, model, item_name, **filter_criteria):
        """
        Reads a single item from the database based on filter criteria.

        Implements request-level caching. If the same query is made multiple
        times in one request, the result is served from the cache.

        Args:
            model (db.Model): The SQLAlchemy model class to query (e.g., Profile).
            item_name (str): A human-readable name for the item (e.g., "Profile").
            **filter_criteria: Keyword arguments to filter by (e.g., email="x@y.com").

        Returns:
            dict: A standardized success or error response dictionary.
        """
        # Create a unique cache key based on the model and filter criteria
        cache_key_parts = [f"{k}-{v}" for k, v in sorted(filter_criteria.items())]
        cache_key = f"{model.__name__}-{'&'.join(cache_key_parts)}"

        # Check if the result is already in the request cache
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            # Build the select statement
            stmt = select(model)

            # Dynamically add 'where' clauses for each filter criterion
            for key, value in filter_criteria.items():
                attribute = getattr(model, key)
                stmt = stmt.where(attribute == value)

            # Execute the query, ensuring uniqueness, and get one result or None
            item = self._session.execute(stmt).unique().scalars().one_or_none()

            # Format the response
            res = success_res(payload={ item_name.lower(): item }, msg=f"{item_name} found") if item else error_res(msg=f"{item_name} not found")

            # If the query was successful, store the result in the cache
            if res.get("success"):
                self._cache[cache_key] = res

            return res

        except Exception as e:
            # Handle any unexpected database errors
            print(f"Unknown error occured. {e}")
            return error_res(msg=f"An unknown error occured {e}")
    
    def read_items(self, model, item_name, **filter_criteria):
        """
        Reads multiple items from the database based on filter criteria.

        Implements request-level caching.

        Args:
            model (db.Model): The SQLAlchemy model class to query (e.g., Thought).
            item_name (str): A human-readable name for the items (e.g., "Thoughts").
            **filter_criteria: Keyword arguments to filter by.

        Returns:
            dict: A standardized success or error response dictionary.
        """
        # Create a unique cache key based on the model and filter criteria
        cache_key_parts = [f"{k}-{v}" for k, v in sorted(filter_criteria.items())]
        cache_key = f"{model.__name__}-{'&'.join(cache_key_parts)}"

        # Check if the result is already in the request cache
        if cache_key in self._cache:
            print("Cached")
            return self._cache[cache_key]
        
        try:
            # Build the select statement
            stmt = select(model)

            # Dynamically add 'where' clauses for each filter criterion
            for key, value in filter_criteria.items():
                attribute = getattr(model, key)
                stmt = stmt.where(attribute == value)

            # Execute the query and get all results
            items = self._session.execute(stmt).unique().scalars().all()

            # Format the response
            res = success_res(payload={ item_name.lower(): items }, msg=f"{item_name} found") if items else error_res(msg=f"{item_name} not found")

            # If the query was successful, store the result in the cache
            if res.get("success"):
                self._cache[cache_key] = res

            return res
        
        except Exception as e:
            return error_res(msg=f"An unknown error occured {e}")

    def create_item(self, item, success_msg, item_name):
        """
        Adds a single new item (model instance) to the database.

        Args:
            item (db.Model): The instantiated SQLAlchemy model to add (e.g., Profile(...)).
            success_msg (str): The message to return on success.
            item_name (str): A human-readable name for error messages.

        Returns:
            dict: A standardized success or error response dictionary.
        """
        try:
            self._session.add(item)
            self._session.commit()
            return success_res(payload={ item_name.lower(): item }, msg=success_msg)
        
        # Error handling
        except IntegrityError as e:
            # Rollback the session to prevent partial/failed transactions
            self._session.rollback()
            return error_res(f"Could not create {item_name} due to database integrity error {e}")

        except Exception as e:
            self._session.rollback()
            return error_res(f"Failed to create {item_name} due to an unknown database error: {e}")
        
    def create_items(self, model, items, success_msg, item_name):
        """
        Adds multiple new items to the database in a single transaction (bulk insert).

        Args:
            model (db.Model): The model class for the items being inserted.
            items (list[dict]): A list of dictionaries, where each dict contains
                                the data for a new item.
            success_msg (str): The message to return on success.
            item_name (str): A human-readable name for error messages.

        Returns:
            dict: A standardized success or error response dictionary.
        """
        try:
            # Use bulk insert for efficiency
            self._session.execute(
                insert(model),
                items
            )
            self._session.commit()
            return success_res(payload={}, msg=success_msg)

        # Error handling
        except IntegrityError as e:
            self._session.rollback()
            return error_res(f"Could not create one or more {item_name}s due to database integrity error {e}")

        except Exception as e:
            self._session.rollback()
            return error_res(f"Failed to create one or more {item_name}s due to an unknown database error: {e}")
        
    def update_item(self, item, item_name, success_msg, **item_kwargs):
        """
        Updates attributes on a single, existing SQLAlchemy model instance.

        This method directly modifies the provided item object and commits it.

        Args:
            item (db.Model): The SQLAlchemy model instance to update.
            item_name (str): A human-readable name for error messages.
            success_msg (str): The message to return on successful update.
            **item_kwargs: Keyword arguments for the fields to update.

        Returns:
            dict: A standardized success or error response dictionary.
        """
        try:
            # Loop through the provided keyword arguments
            for key, value in item_kwargs.items():
                # Check if the model instance actually has this attribute
                if hasattr(item, key):
                    # Update the attribute on the model instance
                    setattr(item, key, value)
            
            # Commit the changes to the database
            self._session.commit()
            return success_res(payload={}, msg=success_msg)

        # Error handling
        except IntegrityError as e:
            self._session.rollback()
            return error_res(f"Could not update {item_name} due to database integrity error {e}")

        except Exception as e:
            self._session.rollback()
            return error_res(f"Failed to update {item_name} due to an unknown database error: {e}")
        

    def update_items(self, model, item_name, success_msg, filter_criteria, update_values):
        """
        Updates multiple items in the database that match filter criteria.

        This performs a bulk 'UPDATE...WHERE...' query.

        Args:
            model (db.Model): The model class to update.
            item_name (str): A human-readable name for error messages.
            success_msg (str): The message to return on success.
            filter_criteria (dict): A dict of columns/values to filter by (the 'WHERE' clause).
            update_values (dict): A dict of columns/values to update.

        Returns:
            dict: A standardized success or error response dictionary.
        """
        if not filter_criteria or not update_values:
            return error_res(f"Missing filter and / or update criteria")

        # Build the 'UPDATE...WHERE...VALUES' statement
        stmt = (
            update(
                (model)
                .where_by(**filter_criteria)  # e.g., .where_by(profile_id=1)
                .values(**update_values)       # e.g., .values(is_active=False)
            )
        )

        try:
            self._session.execute(stmt)
            self._session.commit()
            return success_res(payload={}, msg=success_msg)
        
        # Error handling
        except IntegrityError as e:
            self._session.rollback()
            return error_res(f"Could not update one or more {item_name}s due to database integrity error {e}")

        except Exception as e:
            self._session.rollback()
            return error_res(f"Failed to update one more {item_name}s due to an unknown database error: {e}")

    def delete_item(self, item, item_name, success_msg):
        """
        Deletes a single, existing SQLAlchemy model instance from the database.

        Args:
            item (db.Model): The model instance to delete.
            item_name (str): A human-readable name for error messages.
            success_msg (str): The message to return on success.

        Returns:
            dict: A standardized success or error response dictionary.
        """
        try:
            self._session.delete(item)
            self._session.commit()
            return success_res(payload={}, msg=success_msg)

        # Error handling
        except IntegrityError as e:
            self._session.rollback()
            return error_res(f"Could not delete {item_name} due to database integrity error {e}")

        except Exception as e:
            self._session.rollback()
            return error_res(f"Failed to delete {item_name} due to an unknown database error: {e}")

    def delete_items(self, model, item_name, success_msg, **filter_criteria):
        """
        Deletes multiple items from the database based on filter criteria.

        This performs a bulk 'DELETE...WHERE...' query.

        Args:
            model (db.Model): The model class to delete from.
            item_name (str): A human-readable name for error messages.
            success_msg (str): The message to return on success.
            **filter_criteria: Keyword arguments to filter by (the 'WHERE' clause).

        Returns:
            dict: A standardized success or error response dictionary.
        """
        if not filter_criteria:
            return error_res(f"Missing filter criteria")

        # Build the 'DELETE...WHERE...' statement
        stmt = delete(model).where_by(**filter_criteria)

        try:
            self._session.execute(stmt)
            self._session.commit()
            return success_res(payload={}, msg=success_msg)
            
        # Error handling
        except IntegrityError as e:
            self._session.rollback()
            return error_res(f"Could not delete one or more {item_name}s due to database integrity error {e}")

        except Exception as e:
            self._session.rollback()
            return error_res(f"Failed to delete one more {item_name}s due to an unknown database error: {e}")