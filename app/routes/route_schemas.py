# Schema for a Blueprint
def blueprint_schema(blueprint) -> dict:
    return {
        "is_blueprint": True,
        "blueprint": blueprint
    }

# Schema for a Core Route
def core_schema(rule, endpoint, view_func, methods) -> dict:
    return {
        "is_blueprint": False,
        "rule": rule,
        "endpoint": endpoint,
        "func": view_func,
        "methods": methods
    }