from flask import session
from app.helper.functions.response_schemas import success_res, error_res

class SessionManager:
    _SESSION_PROFILE_KEY: str = "profile_id"

    def __init__(self) -> None:
        print("Session Manager ready...")
    
    def get_logged_in(self) -> dict:
        profile_id = session.get(self._SESSION_PROFILE_KEY, None)
        return success_res(payload={ "profile_id": profile_id  }, msg="Profile Found") if profile_id else error_res(msg="Profile Not Found")

    def login(self, profile_id: int) -> dict:
        session[self._SESSION_PROFILE_KEY] = profile_id
        success = session[self._SESSION_PROFILE_KEY] == profile_id
        return success_res(payload={ "user_id": profile_id }, msg="Profile logged in") if success else error_res(msg="Error logging in profile")

    def logout(self) -> dict:
        profile_id = session.get(self._SESSION_PROFILE_KEY)
        session.pop(self._SESSION_PROFILE_KEY, None)

        return success_res(payload={"logged_out": profile_id}, msg="Profile logged out") if self._SESSION_PROFILE_KEY not in session else error_res(msg="Error logging user out")