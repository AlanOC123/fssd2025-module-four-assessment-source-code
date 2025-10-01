from flask import session
from datetime import datetime, timezone
from pprint import pprint

class SessionManager:
    _SESSION_USER_KEY: str = "user_id"
    _LOG: list = []

    def __init__(self) -> None:
        self._LOG = []
        print("Session Manager ready...")

    def create_res(self, action: str, success_flag: bool, user: int | None) -> dict:
        return {
            "action": action,
            "success": success_flag,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user": user
        }
    
    def update_log_count(self) -> None:
        self._NUM_LOGS = len(self._LOG)

    def print_logs(self) -> None:
        print(f"\n--- SESSION MANAGER LOGS: {len(self._LOG)}--- ")
        for log in self._LOG:
            pprint(log)

    def push_log(self, res: dict) -> None:
        self._LOG.append(res)
        return self.update_log_count()

    def get_last_log(self) -> dict:
        if self._LOG:
            return self._LOG[-1]
        return {}
    
    def get_current_user_id(self) -> int | None:
        user_id = session.get(self._SESSION_USER_KEY)
        return int(user_id) if user_id is not None else None

    def login_user(self, user_id: int) -> dict:
        session[self._SESSION_USER_KEY] = id

        success = session.get(self._SESSION_USER_KEY) == user_id
        res = self.create_res("Logged in", success, user_id)
        self.push_log(res)

        return res

    def logout_user(self):
        user_id = session[self._SESSION_USER_KEY]
        session.pop(self._SESSION_USER_KEY, None)
        success = self._SESSION_USER_KEY not in session

        res = self.create_res("Logged out", success, user_id)
        self.push_log(res)

        return res