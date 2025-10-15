from flask import render_template, redirect, request, url_for, current_app
from . import bp

@bp.route(rule="/sign-in", endpoint="sign_in", methods=["GET", "POST"])
def sign_in():
    method = request.method;

    if method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
    
        if not email or not password:
            error = { "success": False, "msg": "Please fill out all fields" }
            return render_template('pages/auth/sign-in.html', pg_name="sign_in", error=error)

        db_res = current_app.db_manager.profile.get_profile_by_email(email)
        success = db_res.get("success")

        if not success:
            error = { "success": success, "msg": "Invalid email or password" }
            return render_template('pages/auth/sign-in.html', pg_name="sign_in", error=error)

        payload = db_res.get("payload", {})
        profile = payload.get("profile")

        is_correct_password = current_app.db_manager.profile.check_password(profile, password)

        if not is_correct_password:
            error = { "success": success, "msg": "Invalid email or password" }
            return render_template('pages/auth/sign-in.html',pg_name="sign_in", error=error)

        session_res = current_app.session_manager.login_profile(profile.id)

        if not session_res.get("success"):
            error = { "success": False, "msg": session_res.get("msg") }
            render_template('pages/auth/sign-in.html', pg_name="sign_in", error=error)

        return redirect(url_for("index"))
    
    is_logged_in = current_app.session_manager.get_logged_in().get("success")

    if is_logged_in: return redirect(url_for('index'))

    return render_template('pages/auth/sign-in.html', pg_name="sign_in", error=None)

@bp.route(rule="/register", endpoint="register", methods=["POST", "GET"])
def register():
    method = request.method

    if method == "POST":
        email = request.form.get("email", None)
        password = request.form.get("password", None)

        if not email:
            error = { "success": False, "msg": "Please enter an email", "class": None, "id": None  }
            return render_template('pages/auth/register.html', pg_name='register', error=error)
        if not password:   
            error = { "success": False, "msg": "Please create a password", "class": None, "id": None  }
            return render_template('pages/auth/register.html', pg_name='register', error=error)
        
        profile_raw = {
            "email": email,
            "password": password
        }
        
        db_res = current_app.db_manager.profile.create_profile(**profile_raw)
        success = db_res.get("success")

        if not success:
            msg: str = db_res.get("msg", "")
            if "Email" in msg or "email" in msg:
                error = { "success": False, "msg": msg, "class": None, "id": None  }
                return render_template('pages/auth/register.html', pg_name='register', error=error)

            if "Password" in msg or "password" in msg:
                error = { "success": False, "msg": msg, "class": None, "id": None  }
                return render_template('pages/auth/register.html', pg_name='register', error=error)
            
            else:
                error = { "success": False, "msg": msg, "class": None, "id": None  }
                return render_template('pages/auth/register.html', pg_name='register', error=error)

        return redirect(url_for('auth.sign_in'))

    return render_template('pages/auth/register.html', pg_name='register', error=None)