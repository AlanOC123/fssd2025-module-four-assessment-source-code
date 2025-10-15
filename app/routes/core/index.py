from flask import Flask, render_template, redirect, url_for, current_app
from ..route_schemas import core_schema

def index():
    session_res = current_app.session_manager.get_logged_in()

    is_logged_in = session_res.get("success")

    if not is_logged_in:
        return redirect(url_for('auth.sign_in'))

    profile_id = session_res.get("payload").get("profile_id")

    profile_res = current_app.db_manager.profile.get_profile_by_id(profile_id)
    success = profile_res.get("success")

    if not success:
        return redirect(url_for('auth.sign_in'))

    user_selected = current_app.session_manager.get_user_id().get("success")

    if not user_selected:
        return redirect(url_for('users.select'))

    return render_template("pages/core/index.html")

main_index_route = core_schema(rule="/", endpoint="index", methods=["GET"], view_func=index)