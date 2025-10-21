from flask import render_template, redirect, request, url_for, current_app, flash
from . import bp
from datetime import datetime
from app.helper.classes.database.DatabaseManager import DatabaseManager
from app.helper.classes.core.SessionManager import SessionManager

@bp.route(rule="/sign-in", endpoint="sign_in", methods=["GET", "POST"])
def sign_in():
    method = request.method;
    db_manager: DatabaseManager = current_app.db_manager
    session_manager: SessionManager = current_app.session_manager
    print("Signing In...")

    if method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        sign_in_attempt = db_manager.profile.check_sign_in(**{ "email": email, "password": password })

        if not sign_in_attempt.get("success"):
            flash(message=sign_in_attempt.get("msg", ""), category='success')
            return render_template('pages/auth/sign-in.html', pg_name="sign_in")

        session_res = session_manager.login(sign_in_attempt.get("payload", {}).get("profile_id", 0))

        if not session_res.get("success"):
            flash(message=session_res.get("msg", ""), category='error')
            render_template('pages/auth/sign-in.html', pg_name="sign_in")

        flash(message=sign_in_attempt.get("msg", ""), category='success')
        return redirect(url_for("index"))
    
    is_logged_in = session_manager.get_logged_in().get("success")
    if is_logged_in: return redirect(url_for('index'))

    return render_template('pages/auth/sign-in.html', pg_name="sign_in")

@bp.route(rule="/register", endpoint="register", methods=["POST", "GET"])
def register():
    db_manager: DatabaseManager = current_app.db_manager
    session_manager: SessionManager = current_app.session_manager

    session_manager.logout()
    method = request.method

    if method == "POST":
        first_name = request.form.get("first-name")
        surname = request.form.get("surname")
        date_of_birth = request.form.get("dob")
        email = request.form.get("email", None)
        password = request.form.get("password", None)

        profile_raw = {
            "first_name": first_name,
            "surname": surname,
            "date_of_birth": date_of_birth,
            "email": email,
            "password": password,
            "theme_name": "Default"
        }

        db_res = db_manager.profile.create_profile(**profile_raw)

        if not db_res.get("success"):
            flash(message=db_res.get("msg", ""), category='error')
            return render_template('pages/auth/register.html', pg_name='register')

        flash(message="User created successfully", category='success')
        return redirect(url_for('auth.sign_in'))

    return render_template('pages/auth/register.html', pg_name='register')