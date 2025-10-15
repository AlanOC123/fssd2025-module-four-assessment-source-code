from typing import Any

def generic_res(payload: dict[str, Any]={}, msg: str="") -> dict[str, (bool | str | dict)]:
    return {
        "success": False,
        "msg": msg,
        "payload": payload,
    }

def error_res(msg) -> dict:
    return generic_res(msg=msg)

def success_res(payload, msg) -> dict:
    generic = generic_res(payload=payload, msg=msg)
    generic["success"] = True
    generic["payload"] = payload
    return generic