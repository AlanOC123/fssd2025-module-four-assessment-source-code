from flask import Flask, g
from app import get_db
from sqlalchemy import select, insert, update, delete
from app.helper.functions.response_schemas import success_res, error_res
from sqlalchemy.exc import IntegrityError

class BaseManager():
    _db_manager = None
    _app: Flask | None = None

    def __init__(self, app: Flask, db_manager_instance) -> None:
        self._app = app
        self._db_manager = db_manager_instance

        if not self._app:
            raise ValueError("Invalid Database Initialisation. App not provided")
    
    @property
    def _session(self):
        if not "db_session" in g:
            db_object = get_db()
            g.db_session = db_object.session

        return g.db_session

    @property
    def _cache(self):
        if "request_cache" not in g:
            g.request_cache = {}
        
        return g.request_cache
    
    def read_item(self, model, item_name, **filter_criteria):
        cache_key_parts = [f"{k}-{v}" for k, v in sorted(filter_criteria.items())]
        cache_key = f"{model.__name__}-{'&'.join(cache_key_parts)}"

        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            stmt = select(model)

            for key, value in filter_criteria.items():
                attribute = getattr(model, key)
                stmt = stmt.where(attribute == value)

            item = self._session.execute(stmt).unique().scalars().one_or_none()

            res = success_res(payload={ item_name.lower(): item }, msg=f"{item_name} found") if item else error_res(msg=f"{item_name} not found")

            self._cache[cache_key] = res

            return res

        except Exception as e:
            return error_res(msg=f"An unknown error occured {e}")
    
    def read_items(self, model, item_name, **filter_criteria):
        cache_key_parts = [f"{k}-{v}" for k, v in sorted(filter_criteria.items())]
        cache_key = f"{model.__name__}-{'&'.join(cache_key_parts)}"

        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            stmt = select(model)

            for key, value in filter_criteria.items():
                attribute = getattr(model, key)
                stmt = stmt.where(attribute == value)

            items = self._session.execute(stmt).unique().scalars().all()

            res = success_res(payload={ item_name.lower(): items }, msg=f"{item_name} found") if items else error_res(msg=f"{item_name} not found")

            self._cache[cache_key] = res

            return res
        
        except Exception as e:
            return error_res(msg=f"An unknown error occured {e}")

    def create_item(self, item, success_msg, item_name):
        try:
            self._session.add(item)
            self._session.commit()
            return success_res(payload={ item_name.lower(): item }, msg=success_msg)
        
        # Error handling
        except IntegrityError as e:
            self._session.rollback()
            return error_res(f"Could not create {item_name} due to database integrity error {e}")

        except Exception as e:
            self._session.rollback()
            return error_res(f"Failed to create {item_name} due to an unknown database error: {e}")
        
    def create_items(self, model, items, success_msg, item_name):
        try:
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
        

    def update_items(self, model, item_name, success_msg, filter_criteria, update_values):
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

    def delete_item(self, item, item_name, success_msg):
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