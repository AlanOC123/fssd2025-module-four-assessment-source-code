from flask import session
from app.helper.functions.response_schemas import success_res, error_res

class SessionManager:
    _SESSION_IDENTITY_KEY: str = "identity_id"

    def __init__(self) -> None:
        print("Session Manager ready...")

    def set_identity(self, identity_id):
        session[self._SESSION_IDENTITY_KEY] = identity_id
        success = session[self._SESSION_IDENTITY_KEY] == identity_id
        return success_res(payload={ "identity_id": identity_id }, msg="Identity set") if success else error_res(msg="Error setting identity")
    
    def clear_session(self):
        session.clear()