from flask import Flask, g
from app import get_db

class BaseManager():
    __app: Flask | None = None
    __query_cache:dict = {}

    def __init__(self, app: Flask) -> None:
        self.__app = app

        if not self.__app:
            raise ValueError("Invalid Database Initialisation. App not provided")
    
    @property
    def _session(self):
        if not "db_session" in g:
            db_object = get_db()
            g.db_session = db_object.session

        print(g.db_session)

        return g.db_session
    
    def gen_cache_key(self, id, ref):
        return f"{id}-{ref}"
    
    def create_res(self, owner, action, success):
        return {
            "owner": owner,
            "action": action,
            "success": success
        }
    
    def clear_cache(self):
        self.__query_cache.clear()
        return self.__query_cache

    def get_from_cache(self, key):
        return self.__query_cache.get(key, None)

    def add_to_cache(self, key, item, is_success: bool):
        payload = { "res": item, "success": is_success }

        if self.get_from_cache(key) is None:
            self.__query_cache[key] = payload;

    def delete_from_cache(self, key):
        return self.__query_cache.pop(key)