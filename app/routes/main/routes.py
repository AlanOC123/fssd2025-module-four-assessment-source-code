from flask import render_template, redirect, url_for, current_app, flash
from . import app_bp
from flask_login import current_user, login_required

@app_bp.get(rule="/home", endpoint="home")
@login_required
def home():
    return render_template('pages/main/home.html')

@app_bp.get(rule="/projects", endpoint="projects")
@login_required
def projects():
    return render_template('pages/main/projects.html')

@app_bp.get(rule="/tasks", endpoint="tasks")
@login_required
def tasks():
    return render_template('pages/main/tasks.html')

@app_bp.get(rule="/thoughts", endpoint="thoughts")
@login_required
def thoughts():
    return render_template('pages/main/thoughts.html')