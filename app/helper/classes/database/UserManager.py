from flask import Flask
from .BaseManager import BaseManager
from app.database.models import User
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
import os
import bcrypt

class UserManager(BaseManager):
    _is_test_env = False
    _id_key = "u"
    _min_pw_len = 8

    def __init__(self, app: Flask) -> None:
        super().__init__(app)
        env = os.environ.get("FLASK_CONFIG")

        if env in {"testing", "dev"}:
            self._is_test_env = True

    def get_by_id(self, id: int) -> User | None:
        cache_key = self.gen_cache_key(self._id_key, id)
        cached_try = self.get_from_cache(cache_key)

        if cached_try and cached_try.get("success", False):
            return cached_try.get("res")
        elif cached_try and not cached_try.get("success", False):
            print("User not found")
            return None

        stmt = select(User).where(User.id == id)

        try:
            db_session = self._session
            user = db_session.execute(stmt).unique().one_or_none()[0]

            if user:
                self.add_to_cache(cache_key, user, True)
            else:
                self.add_to_cache(cache_key, None, False)
            return user
        except:
            print(f"Failed to get User. {id=}")
            self.add_to_cache(cache_key, None, False)
            return None
    
    def get_by_name(self, user_name: str) -> User | None:
        cache_key = self.gen_cache_key(self._id_key, user_name)
        cached_try = self.get_from_cache(cache_key)

        if cached_try and cached_try.get("success", False):
            return cached_try.get("res")
        elif cached_try and not cached_try.get("success", False):
            print("User not found")
            return None

        stmt = select(User).where(User.user_name == user_name)

        try:
            db_session = self._session
            user = db_session.execute(stmt).unique().one_or_none()[0]

            if user:
                self.add_to_cache(cache_key, user, True)
            else:
                self.add_to_cache(cache_key, None, False)
            return user
        except Exception as e:
            print(f"Failed to get User. {user_name=}, {e=}")
            self.add_to_cache(cache_key, None, False)
            return None

    @property
    def admin(self) -> User | None:
        if not self._is_test_env:
            pass
        return self.get_by_name("AdminUser")
    
    @property
    def admin_id(self) -> int:
        admin_user = self.admin
        return admin_user.id if admin_user else 0
    
    def hash_password(self, password: str):
        bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hash = bcrypt.hashpw(bytes, salt)
        return hash

    def validate_password(self, password: str):
        from string import punctuation
        length_ok = len(password) >= self._min_pw_len
        has_special = any(c in punctuation for c in password)
        has_cap = any(c.isupper() for c in password)

        if (not length_ok or not has_special or not has_cap):
            return False
        
        return True
    
    def create_user(self, user_name: str, password: str) -> None:
        valid_password = self.validate_password(password)

        if not valid_password:
            raise ValueError("Password doesnt meet minimum complexity requirements")
        
        if self.get_by_name(user_name):
            raise ValueError(f"Username {user_name} is taken")

        hashpw = self.hash_password(password)
        user = User(user_name=user_name, password_hash=hashpw)

        try:
            self._session.add(user)
            self._session.commit()
        except IntegrityError:
            self._session.rollback()
            raise RuntimeError("Could not create user due to database integrity error")
        except Exception as e:
            raise RuntimeError(f"Failed to create user due to an unknown database error: {e}")

