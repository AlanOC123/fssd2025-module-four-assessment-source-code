from . import bp
from flask import request
from app import db_manager

@bp.post(rule="/create-user", endpoint="create_user")
def create_user():
    user_name = request.form.get("user-name")
    password = request.form.get("password")
    print(user_name)
    print(password)

    db_manager.user.create_user(user_name=user_name, password=password)
    return {

    }, 200
