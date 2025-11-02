from flask import render_template, redirect, url_for, current_app, flash, abort, request
from . import app_bp
from flask_login import current_user, login_required
from .helpers import get_identities, get_ordinal_suffix
from .forms import CreateThoughtForm, SwitchIdentityForm
from app.helper.classes.database.DatabaseManager import DatabaseManager
from app.helper.classes.database.ProfileManager import ProfileManager
from app.helper.classes.database.ProfileIdentityManager import ProfileIdentityManager
from app.helper.classes.database.ThoughtManager import ThoughtManager
from app.database.models import Profile, Thought, ProfileIdentity
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
    return render_template(
        'pages/main/projects.html',
        pg_name="projects",
        current_user=current_user
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

    # Switch Identity Form Submit
    if switch_identity_form.submit_identity.data and switch_identity_form.validate_on_submit():

        # Get the identity
        identity_id = switch_identity_form.select_identity.data

        # Set and swap the identity
        active_identity_res = profile_identity_manager.set_identity(current_user, identity_id)

        if not active_identity_res.get("success", False):
            print(f"Error setting identity. Error: {db_res.get("msg", "")}")
        
        active_identity = active_identity_res.get("payload", {}).get("active_identity")
        print("Identity correctly set...")

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