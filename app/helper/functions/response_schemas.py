"""
Defines standardized response schemas for the application's managers.

This file provides helper functions to create consistent dictionary
responses (e.g., for success or error) from all database manager
methods. This ensures that the routes and API endpoints
receive a predictable data structure.
"""

from typing import Any

def generic_res(payload: dict[str, Any]={}, msg: str="") -> dict[str, (bool | str | dict)]:
    """
    Creates a generic, base response dictionary.

    This is the foundation for the other response helpers.
    It intentionally defaults to 'success: False'.

    Args:
        payload (dict, optional): Any data to include in the response. Defaults to {}.
        msg (str, optional): A descriptive message. Defaults to "".

    Returns:
        dict: A standardized response dictionary.
    """
    return {
        "success": False,
        "msg": msg,
        "payload": payload,
    }

def error_res(msg) -> dict:
    """
    Creates a standardized error response.

    This is a shortcut for generic_res() that only requires an error
    message and always returns 'success: False'.

    Args:
        msg (str): The error message to return.

    Returns:
        dict: A standardized error response dictionary.
    """
    return generic_res(msg=msg)

def success_res(payload, msg) -> dict:
    """
    Creates a standardized success response.

    This is a shortcut that calls generic_res() and then
    overwrites the 'success' key to be True.

    Args:
        payload (dict): The data to include in the response.
        msg (str): The success message.

    Returns:
        dict: A standardized success response dictionary.
    """
    # Get the base dictionary (which has success: False)
    generic = generic_res(payload=payload, msg=msg)
    
    # Overwrite the success key
    generic["success"] = True
    
    # Note: You are setting the payload twice (once in generic_res and
    # once here), but it doesn't cause any harm.
    generic["payload"] = payload
    return generic