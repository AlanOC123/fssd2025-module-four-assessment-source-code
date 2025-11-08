from flask import Flask, g
from app import get_db
from sqlalchemy import select, insert, update, delete
from app.helper.functions.response_schemas import success_res, error_res
from sqlalchemy.exc import IntegrityError

class BaseManager():
    # Init the db instance
    def __init__(self, db_manager_instance) -> None:
        from app.helper.classes.database.DatabaseManager import DatabaseManager
        self._db_manager: DatabaseManager = db_manager_instance
    
    # Easy access to current connection
    @property
    def _session(self):
        """
        Gets the db connection from the current g object 
        """
        if not "db_session" in g:
            db_object = get_db()
            g.db_session = db_object.session

        return g.db_session

    # Cache responses for speed if necessary
    @property
    def _cache(self) -> dict:
        """
        Allows access to the cache
        """
        if "request_cache" not in g:
            g.request_cache = {}
        
        return g.request_cache
    
    # Read generic, simple items
    def read_item(self, model, item_name, **filter_criteria) -> dict:
        """
        Simple read operations with basic filtering. Checks the cache first then queries the db on the existing connection. Returns a single item.
        """
        # Build a cache query
        cache_key_parts = [f"{k}-{v}" for k, v in sorted(filter_criteria.items())]
        cache_key = f"{model.__name__}-{'&'.join(cache_key_parts)}"

        # Check the cache
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            # Create the query
            stmt = select(model)

            # Check for filters and modify the query
            for key, value in filter_criteria.items():
                attribute = getattr(model, key)
                stmt = stmt.where(attribute == value)

            # Get the first item
            item = self._session.execute(stmt).unique().scalars().one_or_none()

            # Return the item
            res = success_res(payload={ item_name.lower(): item }, msg=f"{item_name} found") if item else error_res(msg=f"{item_name} not found")

            if res.get("success"):
                self._cache[cache_key] = res

            return res

        # Handle errors
        except Exception as e:
            print(f"Unknown error occured. {e}")
            return error_res(msg=f"An unknown error occured {e}")
    
    def read_items(self, model, item_name, **filter_criteria) -> dict:
        """
        Simple read operations with basic filtering. Checks the cache first then queries the db on the existing connection. Returns multiple items.
        """
        cache_key_parts = [f"{k}-{v}" for k, v in sorted(filter_criteria.items())]
        cache_key = f"{model.__name__}-{'&'.join(cache_key_parts)}"

        if cache_key in self._cache:
            print("Cached")
            return self._cache[cache_key]
        
        try:
            stmt = select(model)

            for key, value in filter_criteria.items():
                attribute = getattr(model, key)
                stmt = stmt.where(attribute == value)

            items = self._session.execute(stmt).unique().scalars().all()

            res = success_res(payload={ item_name.lower(): items }, msg=f"{item_name} found") if items else error_res(msg=f"{item_name} not found")

            if res.get("success"):
                self._cache[cache_key] = res

            return res
        
        except Exception as e:
            return error_res(msg=f"An unknown error occured {e}")

    def create_item(self, item, success_msg, item_name) -> dict:
        """
        Simple create operations. Creates single items.
        """
        try:
            self._session.add(item)
            self._session.commit()
            return success_res(payload={ item_name.lower(): item }, msg=success_msg)
        
        # Error handling with a session rollback to revert to a stable base
        except IntegrityError as e:
            self._session.rollback()
            return error_res(f"Could not create {item_name} due to database integrity error {e}")

        except Exception as e:
            self._session.rollback()
            return error_res(f"Failed to create {item_name} due to an unknown database error: {e}")
        
    def create_items(self, model, items, success_msg, item_name) -> dict:
        """
        Simple create operations. Creates multiple items.
        """
        try:
            self._session.execute(
                insert(model),
                items
            )
            self._session.commit()
            return success_res(payload={}, msg=success_msg)

        except IntegrityError as e:
            self._session.rollback()
            return error_res(f"Could not create one or more {item_name}s due to database integrity error {e}")

        except Exception as e:
            self._session.rollback()
            return error_res(f"Failed to create one or more {item_name}s due to an unknown database error: {e}")
        
    def update_item(self, item, item_name, success_msg, **item_kwargs) -> dict:
        """
        Simple update operations. Updates single items.
        """
        try:
            for key, value in item_kwargs.items():
                if hasattr(item, key):
                    setattr(item, key, value)
            
            self._session.commit()
            return success_res(payload={}, msg=success_msg)

        # Error handling
        except IntegrityError as e:
            self._session.rollback()
            return error_res(f"Could not update {item_name} due to database integrity error {e}")

        except Exception as e:
            self._session.rollback()
            return error_res(f"Failed to update {item_name} due to an unknown database error: {e}")
        

    def update_items(self, model, item_name, success_msg, filter_criteria, update_values) -> dict:
        # Early return if no update filter criteria given
        if not filter_criteria or not update_values:
            return error_res(f"Missing filter and / or update criteria")

        stmt = (
            update(
                (model)
                .where_by(**filter_criteria)
                .values(**update_values)
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

    def delete_item(self, item, item_name, success_msg) -> dict:
        """
        Simple delete operations. Allows basic filtering. Deletes single items.
        """
        try:
            self._session.delete(item)
            self._session.commit()
            return success_res(payload={}, msg=success_msg)

        except IntegrityError as e:
            self._session.rollback()
            return error_res(f"Could not delete {item_name} due to database integrity error {e}")

        except Exception as e:
            self._session.rollback()
            return error_res(f"Failed to delete {item_name} due to an unknown database error: {e}")

    def delete_items(self, model, item_name, success_msg, **filter_criteria):
        """
        Simple delete operations. Allows basic filtering. Deletes single items.
        """
        if not filter_criteria:
            return error_res(f"Missing filter criteria")

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