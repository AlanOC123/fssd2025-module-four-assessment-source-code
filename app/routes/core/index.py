from flask import Flask, render_template, redirect, url_for
from app import db_manager, session_manager
from ..route_schemas import core_schema

def index():
    if not session_manager.get_current_user_id():
        return redirect(url_for('auth.sign_in'))
    return "<h1>Hello Person<h1>"

main_index_route = core_schema(rule="/", endpoint="index", methods=["GET"], view_func=index)