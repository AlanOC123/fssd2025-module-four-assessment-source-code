from flask import render_template, session, redirect

from . import bp

@bp.get(rule="/sign-in", endpoint="sign_in")
def sign_in():
    return render_template('pages/auth/sign-in.html')

@bp.get(rule="/register", endpoint="register")
def register():
    return render_template('pages/auth/register.html')