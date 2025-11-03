from flask import render_template, redirect, url_for, current_app, flash, abort, request
from . import app_bp
from flask_login import current_user, login_required
from .helpers import get_identities, get_ordinal_suffix
from .forms import CreateThoughtForm, SwitchIdentityForm, CreateProjectForm
from app.helper.classes.database.DatabaseManager import DatabaseManager
from app.helper.classes.database.ProfileManager import ProfileManager
from app.helper.classes.database.ProfileIdentityManager import ProfileIdentityManager
from app.helper.classes.database.ThoughtManager import ThoughtManager
from app.helper.classes.database.ProjectManager import ProjectManager
from app.database.models import Profile, Thought, ProfileIdentity, Status, Project
from typing import List

@app_bp.get(rule="/home", endpoint="home")
@login_required
def home():
    return render_template(
        'pages/main/home.html', 
        pg_name="home",
        current_user=current_user
    )

@app_bp.route(rule="/projects", endpoint="projects", methods=["GET", "POST"])
@login_required
def projects():
    # Get managers
    db_manager: DatabaseManager = current_app.db_manager
    project_manager: ProjectManager = db_manager.project
    profile_identity_manager: ProfileIdentityManager = db_manager.profile_identity

    # Get the filter
    filter_keyword = request.args.get("filter_key")

    # Query the current identity (Get)
    active_identity_res = profile_identity_manager.get_active_identity(current_user)

    if not active_identity_res.get("success", False):
        active_identity_res = profile_identity_manager.set_default_identity(current_user)

    if not active_identity_res.get("success", False):
        abort(500)
    
    active_identity: ProfileIdentity = active_identity_res.get("payload", {}).get("active_identity")

    # Get all the identities
    all_identities = current_user.identities

    # Create the forms
    project_status_choices = [(e.value, e.name.replace("_", " ").title()) for e in Status]
    identity_choices = [
        (identity.id, (identity.custom_name if identity.custom_name else identity.template.name)) for identity in all_identities 
    ]

    create_project_form = CreateProjectForm(status=project_status_choices)
    switch_identity_form = SwitchIdentityForm(identities=identity_choices)

    projects_res = project_manager.get_projects_by_status(current_user.id, active_identity.id, status_key=filter_keyword)

    if not projects_res.get("success"):
        print(projects_res.get("msg", ""))
        flash("Error getting projects...")
        return render_template(
            'pages/main/projects.html',
            pg_name="projects",
            current_user=current_user,
            active_identity=active_identity,
            create_project_form=create_project_form,
            switch_identity_form=switch_identity_form,
            all_identities=all_identities,
            projects=[]
        )
    
    projects_list = projects_res.get("payload", {}).get("projects", [])

    sorted_projects = sorted(
        projects_list,
        key=lambda project: project.time_left
    )

    # Create Project Form Submit
    if create_project_form.submit_project.data and create_project_form.validate_on_submit():
        project_name = create_project_form.project_name.data;
        project_description = create_project_form.project_description.data;
        project_start_date = create_project_form.project_start_date.data;
        project_end_date = create_project_form.project_end_date.data;
        project_status = create_project_form.project_status.data;

        project_data = {
            "name": project_name,
            "description": project_description,
            "start_date": project_start_date,
            "end_date": project_end_date,
            "status": project_status,
            "owner_id": current_user.id,
            "identity_id": active_identity.id
        }
    
        db_res = project_manager.create_project(**project_data)

        if not db_res.get("success"):
            flash(message="Failed to create project...")
        else:
            flash("Project created!")
        
        return redirect(url_for('app.projects'))

    # Switch Identity Form Submit
    if switch_identity_form.submit_identity.data and switch_identity_form.validate_on_submit():

        # Get the identity
        identity_id = switch_identity_form.select_identity.data

        # Set and swap the identity
        active_identity_res = profile_identity_manager.set_identity(current_user, identity_id)

        if not active_identity_res.get("success", False):
            print(f"Error setting identity. Error: {active_identity_res.get("msg", "")}")
            flash(message="Couldnt set identity...", category="error")
        else:
            active_identity = active_identity_res.get("payload", {}).get("active_identity")
            flash(message="Identity changed!", category="success")
        
        return redirect(url_for('app.projects'))

    return render_template(
        'pages/main/projects.html',
        pg_name="projects",
        current_user=current_user,
        active_identity=active_identity,
        create_project_form=create_project_form,
        switch_identity_form=switch_identity_form,
        all_identities=all_identities,
        projects=sorted_projects
    )

@app_bp.route(rule="/tasks", endpoint="tasks", methods=["GET", "POST"])
@login_required
def tasks():
    
    return render_template(
        'pages/main/tasks.html',
        pg_name="tasks",
        current_user=current_user
    )

@app_bp.route(rule="/thoughts", endpoint="thoughts", methods=["GET", "POST"])
@login_required
def thoughts():
    # Get managers
    db_manager: DatabaseManager = current_app.db_manager
    profile_manager: ProfileManager = db_manager.profile
    profile_identity_manager: ProfileIdentityManager = db_manager.profile_identity
    thought_manager: ThoughtManager = db_manager.thought

    # Query the current identity (Get)
    active_identity_res = profile_identity_manager.get_active_identity(current_user)

    if not active_identity_res.get("success", False):
        active_identity_res = profile_identity_manager.set_default_identity(current_user)

    if not active_identity_res.get("success", False):
        abort(500)
    
    active_identity: ProfileIdentity = active_identity_res.get("payload", {}).get("active_identity")

    # Get all the identities
    all_identities = current_user.identities

    # Create the forms
    create_thought_form = CreateThoughtForm()

    identity_choices = [
        (identity.id, (identity.custom_name if identity.custom_name else identity.template.name)) for identity in all_identities 
    ]

    switch_identity_form = SwitchIdentityForm(identities=identity_choices)

    # Create Thought Form Submit
    if create_thought_form.submit_thought.data and create_thought_form.validate_on_submit():
        content = create_thought_form.create_thought.data;
        db_res = thought_manager.create_thought(profile=current_user, profile_identity=active_identity, content=content)

        if not db_res.get("success", False):
            flash(message="Error creating thought...", category="error")

        return redirect(url_for('app.thoughts'))

    # Switch Identity Form Submit
    if switch_identity_form.submit_identity.data and switch_identity_form.validate_on_submit():

        # Get the identity
        identity_id = switch_identity_form.select_identity.data

        # Set and swap the identity
        active_identity_res = profile_identity_manager.set_identity(current_user, identity_id)

        if not active_identity_res.get("success", False):
            print(f"Error setting identity. Error: {active_identity_res.get("msg", "")}")
            flash(message="Couldnt set identity...", category="error")
        else:
            active_identity = active_identity_res.get("payload", {}).get("active_identity")
            flash(message="Identity changed!", category="success")
        
        return redirect(url_for('app.thoughts'))

    thoughts: List[Thought] = active_identity.thoughts

    timeline_month_set = set()

    for thought in thoughts:
        timeline_month_set.add(
            (
                thought.created_at.year,
                thought.created_at.month,
                thought.created_at.strftime("%B")
            )
        )
    
    timeline_month_sorted = sorted(
        list(timeline_month_set),
        key=lambda x: (x[0], x[1]),
        reverse=True
    )

    filters = {
        "year": request.args.get("year", type=int),
        "month": request.args.get("month", type=int)
    }

    ordered_thoughts_res = thought_manager.get_ordered_thoughts(active_identity.id, **filters)

    ordered_thoughts: List[Thought] = ordered_thoughts_res.get("payload", {}).get("thoughts", [])

    thought_groupings = {}

    for thought in ordered_thoughts:
        suffix = get_ordinal_suffix(thought.created_at.day)
        day_key = thought.created_at.strftime(f'%A %-d{suffix} %B %Y')
        hour_key = thought.created_at.strftime('%H:00')
        new_entry = {
            "time": thought.created_at.strftime('%H:%M'),
            "thought_obj": thought
        }
        day_group = thought_groupings.setdefault(day_key, {})
        hour_group = day_group.setdefault(hour_key, [])
        hour_group.append(new_entry)

    print(thought_groupings)

    return render_template(
        'pages/main/thoughts.html',
        pg_name="thoughts",
        current_user=current_user,
        active_identity=active_identity,
        timeline_data=timeline_month_sorted,
        thought_groupings=thought_groupings,
        switch_identity_form=switch_identity_form,
        all_identities=all_identities,
        create_thought_form=create_thought_form
    )