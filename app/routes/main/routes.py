from flask import render_template, redirect, url_for, current_app, flash
from . import app_bp
from flask_login import current_user, login_required
from .helpers import get_identities

@app_bp.get(rule="/home", endpoint="home")
@login_required
def home():
    identities = get_identities(current_user)
    all_identities = identities.get("all")
    active_identity = identities.get("active")
    return render_template(
        'pages/main/home.html', 
        active_identity=active_identity, 
        identities=all_identities,
        pg_name="home"
    )

@app_bp.route(rule="/projects", endpoint="projects", methods=["GET", "POST"])
@login_required
def projects():
    return render_template(
        'pages/main/projects.html',
        pg_name="projects"
    )

@app_bp.route(rule="/tasks", endpoint="tasks", methods=["GET", "POST"])
@login_required
def tasks():
    return render_template(
        'pages/main/tasks.html',
        pg_name="tasks"
    )

@app_bp.route(rule="/thoughts", endpoint="thoughts", methods=["GET", "POST"])
@login_required
def thoughts():
    return render_template(
        'pages/main/thoughts.html',
        pg_name="thoughts"
    )