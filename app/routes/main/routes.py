"""
Defines the main routes for the logged-in application experience.

This file contains the view functions for the 'app' blueprint, which
handles the main pages:
- /home (Dashboard)
- /projects (Project Management)
- /tasks (Task Management)
- /thoughts (Thoughts Journal)

These routes handle complex logic, including processing multiple forms on
a single page, filtering data, and preparing data for templates.
"""

from flask import render_template, redirect, url_for, current_app, flash, abort, request
from . import app_bp
from flask_login import current_user, login_required
from .helpers import get_identities, get_ordinal_suffix
from .forms import CreateThoughtForm, SwitchIdentityForm, CreateProjectForm, CreateTaskForm, SwitchProjectForm
from app.helper.classes.database.DatabaseManager import DatabaseManager
from app.helper.classes.database.ProfileManager import ProfileManager
from app.helper.classes.database.ProfileIdentityManager import ProfileIdentityManager
from app.helper.classes.database.ThoughtManager import ThoughtManager
from app.helper.classes.database.ProjectManager import ProjectManager
from app.helper.classes.database.TaskManager import TaskManager
from app.database.models import Profile, Thought, ProfileIdentity, Status, Project, Task, Difficulty
from typing import List
from datetime import date

@app_bp.get(rule="/home", endpoint="home")
@login_required
def home():
    """
    Renders the main dashboard (Home) page.

    **Route:** /app/home
    **Method:** GET
    **Protection:** @login_required

    This route performs a significant amount of data aggregation
    by iterating through all of the user's identities, projects, and
    tasks to build data for the dashboard widgets:
    - Identity Widget: Shows all identities and their active project status.
    - Task Widget: Calculates the distribution of tasks by difficulty.
    - Agenda Widget: Finds all incomplete tasks due today.
    - Stats Widget: Counts total projects and tasks (complete/incomplete).
    
    It then renders the 'home.html' template with this processed data.
    """
    user_logged_in: Profile = current_user 
    identities: List[ProfileIdentity] = user_logged_in.identities

    # --- 1. Initialize data structures for widgets ---
    identity_widget_data = []
    task_widget_data = {
        "total_tasks": {"count": 0, "percentage": 100, "legend_key": "total"},
        "easy_tasks": {"count": 0, "percentage": 0, "legend_key": "easy"},
        "medium_tasks": {"count": 0, "percentage": 0, "legend_key": "medium"},
        "hard_tasks": {"count": 0, "percentage": 0, "legend_key": "hard"},
    }
    agenda_widget_data = []
    stats_widget_data = {
        "total_projects": {"count": 0, "label": "Total Projects"},
        "tasks_complete": {"count": 0, "label": "Completed Tasks"},
        "tasks_incomplete": {"count": 0, "label": "Incomplete Tasks"}
    }
    today = date.today()

    # --- 2. Process all data in a single loop ---
    # This is more efficient than multiple separate DB queries.
    for identity in identities:
        # --- 2a. Process Identity Widget Data ---
        identity_data = {
            "img": f"{url_for('static', filename='assets/avatars/')}{identity.template.image}",
            "name": identity.custom_name if identity.custom_name else identity.template.name,
            "active_project": None,
            "num_projects": len(identity.projects)
        }

        active_project: Project | None = None
        stats_widget_data["total_projects"]["count"] += len(identity.projects)

        # Find the active project for this identity
        for project in identity.projects:
            if project.is_active:
                active_project = project
                identity_data["active_project"] = active_project
                identity_widget_data.append(identity_data)
                break
        
        # --- 2b. Process Task, Agenda, and Stats Widget Data ---
        for project in identity.projects:
            for task in project.tasks:
                # Stats Widget
                if task.is_complete:
                    stats_widget_data["tasks_complete"]["count"] += 1
                else:
                    stats_widget_data["tasks_incomplete"]["count"] += 1
                
                # Agenda Widget (only tasks due today and not done)
                if not task.is_complete and task.due_date == today:
                    agenda_widget_data.append(task)
                
                # Task Widget (total count)
                task_widget_data["total_tasks"]["count"] += 1

                # Task Widget (difficulty count)
                if task.difficulty == Difficulty.EASY:
                    task_widget_data["easy_tasks"]["count"] += 1
                elif task.difficulty == Difficulty.MEDIUM:
                    task_widget_data["medium_tasks"]["count"] += 1
                else:
                    task_widget_data["hard_tasks"]["count"] += 1
        
        # If no active project was found for this identity,
        # still add it to the widget list (just without a project).
        if not active_project:
            identity_widget_data.append(identity_data)
    
    # --- 3. Calculate Task Widget Percentages ---
    total_tasks = task_widget_data["total_tasks"]["count"]
    if total_tasks > 0: # Avoid ZeroDivisionError
        for key, value in task_widget_data.items():
            if key == "total_tasks":
                continue
            if value["count"] > 0:
                value["percentage"] = float(value["count"] / total_tasks) * 100
                task_widget_data[key] = value

    # --- 4. Render the dashboard template ---
    return render_template(
        'pages/main/home.html', 
        pg_name="home",
        current_user=user_logged_in,
        identity_widget=identity_widget_data,
        task_widget_data=task_widget_data,
        agenda_widget_data=agenda_widget_data,
        stats_widget_data=stats_widget_data
    )

@app_bp.route(rule="/projects", endpoint="projects", methods=["GET", "POST"])
@login_required
def projects():
    """
    Renders the Projects page and handles form submissions for
    creating new projects and switching the active identity.

    **GET Request:**
    - Renders the projects.html template.
    - Gets the active identity (or sets a default).
    - Fetches all projects for that identity.
    - Filters projects if a 'filter_key' (e.g., 'not_started')
      is provided as a URL query parameter.
    
    **POST Request:**
    - Handles two separate forms:
        1. **CreateProjectForm**: Validates and creates a new project,
           then redirects back to the Projects page.
        2. **SwitchIdentityForm**: Validates and sets the new active
           identity in the session, then redirects back.
    """
    # --- 1. Get managers ---
    db_manager: DatabaseManager = current_app.db_manager
    project_manager: ProjectManager = db_manager.project
    profile_identity_manager: ProfileIdentityManager = db_manager.profile_identity

    # --- 2. Get active identity (or set default) ---
    filter_keyword = request.args.get("filter_key")
    active_identity_res = profile_identity_manager.get_active_identity(current_user)
    if not active_identity_res.get("success", False):
        active_identity_res = profile_identity_manager.set_default_identity(current_user)
    if not active_identity_res.get("success", False):
        abort(500) # Abort if we still can't get an identity
    
    active_identity: ProfileIdentity = active_identity_res.get("payload", {}).get("active_identity")

    # --- 3. Initialize Forms ---
    all_identities = current_user.identities
    identity_choices = [(id.id, (id.custom_name if id.custom_name else id.template.name)) for id in all_identities]

    create_project_form = CreateProjectForm()
    switch_identity_form = SwitchIdentityForm(identities=identity_choices)

    # --- 4. Handle POST Requests (Form Submissions) ---
    
    # Check if the "Create Project" form was submitted
    print(create_project_form.submit_project.data)
    if create_project_form.submit_project.data and create_project_form.validate_on_submit():
        project_data = {
            "name": create_project_form.project_name.data,
            "description": create_project_form.project_description.data,
            "start_date": create_project_form.project_start_date.data,
            "end_date": create_project_form.project_end_date.data,
            "owner_id": current_user.id,
            "identity_id": active_identity.id
        }
        db_res = project_manager.create_project(**project_data)

        if not db_res.get("success"):
            flash(message="Failed to create project...")
        else:
            flash("Project created!")
        
        return redirect(url_for('app.projects'))

    # Check if the "Switch Identity" form was submitted
    if switch_identity_form.submit_identity.data and switch_identity_form.validate_on_submit():
        identity_id = switch_identity_form.select_identity.data
        
        # Call the manager to set the new identity
        active_identity_res = profile_identity_manager.set_identity(current_user, identity_id)

        if not active_identity_res.get("success", False):
            flash(message="Couldnt set identity...", category="error")
        else:
            active_identity = active_identity_res.get("payload", {}).get("active_identity")
            flash(message="Identity changed!", category="success")
        
        return redirect(url_for('app.projects'))

    # --- 5. Handle GET Request (Page Load) ---
    
    # Get projects for the active identity, applying any status filters
    projects_res = project_manager.get_projects_by_status(current_user.id, active_identity.id, status_key=filter_keyword)
    projects_list = projects_res.get("payload", {}).get("projects", [])

    if not projects_res.get("success"):
        flash("Error getting projects...")
    
    # Sort projects by the 'time_left' property
    sorted_projects = sorted(
        projects_list,
        key=lambda project: project.time_left
    )

    return render_template(
        'pages/main/projects.html',
        pg_name="projects",
        current_user=current_user,
        active_identity=active_identity,
        create_project_form=create_project_form,
        switch_identity_form=switch_identity_form,
        all_identities=all_identities,
        projects=sorted_projects,
        filter_keyword=filter_keyword
    )

@app_bp.route(rule="/tasks", endpoint="tasks", methods=["GET", "POST"])
@login_required
def tasks():
    """
    Renders the Tasks page and handles form submissions for
    creating tasks, switching identities, and switching projects.

    **GET Request:**
    - Renders the tasks.html template.
    - Gets the active identity (or sets a default).
    - Gets the active project for that identity (or sets a default).
    - Fetches all tasks for that project.
    - Filters tasks if a 'filter_key' (e.g., 'easy')
      is provided as a URL query parameter.
    
    **POST Request:**
    - Handles THREE separate forms, processed in order:
        1. **CreateTaskForm**: Creates a new task for the active project.
        2. **SwitchIdentityForm**: Sets a new active identity.
        3. **SwitchProjectForm**: Sets a new active project.
    - Redirects back to the Tasks page after any successful POST.
    """
    # --- 1. Get managers ---
    db_manager: DatabaseManager = current_app.db_manager
    project_manager: ProjectManager = db_manager.project
    profile_identity_manager: ProfileIdentityManager = db_manager.profile_identity
    task_manager: TaskManager = db_manager.task

    # --- 2. Get active identity and project ---
    filter_keyword = request.args.get("filter_key")

    # Get active identity
    active_identity_res = profile_identity_manager.get_active_identity(current_user)
    if not active_identity_res.get("success", False):
        active_identity_res = profile_identity_manager.set_default_identity(current_user)
    if not active_identity_res.get("success", False):
        abort(500)
    
    all_identities = current_user.identities
    active_identity: ProfileIdentity = active_identity_res.get("payload", {}).get("active_identity")

    # Get active project (for this identity)
    projects = active_identity.projects
    active_project_res = project_manager.get_active_project(active_identity)
    if not active_project_res.get("success"):
        # This is fine, user might just have no projects
        pass
    
    active_project = active_project_res.get("payload", {}).get("active_project")

    # --- 3. Initialize Forms ---
    task_difficulty_choices = [(e.value, e.name.title()) for e in Difficulty]
    project_choices = [(p.id, p.name) for p in projects]
    identity_choices = [(id.id, (id.custom_name if id.custom_name else id.template.name)) for id in all_identities]

    create_task_form = CreateTaskForm(difficulty_choices=task_difficulty_choices)
    switch_identity_form = SwitchIdentityForm(identities=identity_choices)
    switch_project_form = SwitchProjectForm(project_choices=project_choices)

    # --- 4. Handle POST Requests (Form Submissions) ---
    
    # Check if the "Create Task" form was submitted
    if create_task_form.submit_task.data and create_task_form.validate_on_submit() and active_project:
        task_data = {
            "name": create_task_form.task_name.data,
            "due_date": create_task_form.task_due_date.data,
            "difficulty": create_task_form.task_difficulty.data,
            "project_id": active_project.id
        }
        # This manager method is an atomic transaction
        db_res = task_manager.create_task(**task_data)

        if not db_res.get("success"):
            flash(message="Failed to create task...", category="error")
        else:
            flash("Task created!", category="success")
        
        return redirect(url_for('app.tasks'))

    # Check if the "Switch Identity" form was submitted
    elif switch_identity_form.submit_identity.data and switch_identity_form.validate_on_submit():
        identity_id = switch_identity_form.select_identity.data
        
        # Set the new identity
        active_identity_res = profile_identity_manager.set_identity(current_user, identity_id)

        if not active_identity_res.get("success", False):
            flash(message="Couldnt set identity...", category="error")
        else:
            active_identity = active_identity_res.get("payload", {}).get("active_identity")
            flash(message="Identity changed!", category="success")
        
        return redirect(url_for('app.tasks'))

    # Check if the "Switch Project" form was submitted
    elif switch_project_form.submit_project_switch.data and switch_project_form.validate_on_submit():
        project_id = switch_project_form.switch_project.data

        # Set the new active project
        active_project_res = project_manager.set_active_project(active_identity, project_id)

        if not active_project_res.get("success", False):
            flash(message="Couldnt set project...", category="error")
        else:
            active_project = active_project_res.get("payload", {}).get("active_project")
            flash(message="Project changed!", category="success")

        return redirect(url_for('app.tasks'))
    
    # --- 5. Handle GET Request (Page Load) ---
    tasks = []
    if active_project:
        # Get tasks for the active project, applying any difficulty filters
        tasks_res = task_manager.get_tasks_by_difficulty(active_project.id, difficulty_key=filter_keyword)
        tasks = tasks_res.get("payload", {}).get("tasks", [])
        
        # Sort tasks by the 'time_left' property
        tasks = sorted(
            tasks,
            key=lambda task: task.time_left
        )

    return render_template(
        'pages/main/tasks.html',
        pg_name="tasks",
        current_user=current_user,
        create_task_form=create_task_form,
        switch_identity_form = switch_identity_form,
        switch_project_form=switch_project_form,
        active_identity=active_identity,
        active_project=active_project,
        all_identities=all_identities,
        tasks=tasks,
        filter_keyword=filter_keyword
    )

@app_bp.route(rule="/thoughts", endpoint="thoughts", methods=["GET", "POST"])
@login_required
def thoughts():
    """
    Renders the Thoughts page and handles form submissions for
    creating new thoughts and switching the active identity.

    **GET Request:**
    - Renders the thoughts.html template.
    - Gets the active identity (or sets a default).
    - Fetches all thoughts for that identity.
    - Filters thoughts if 'year' and 'month' are provided as
      URL query parameters (for the timeline).
    - **Groups thoughts by day and hour** for display in the template.
    
    **POST Request:**
    - Handles two separate forms:
        1. **CreateThoughtForm**: Creates a new thought for the active identity.
        2. **SwitchIdentityForm**: Sets a new active identity in the session.
    - Redirects back to the Thoughts page after any successful POST.
    """
    # --- 1. Get managers ---
    db_manager: DatabaseManager = current_app.db_manager
    profile_manager: ProfileManager = db_manager.profile
    profile_identity_manager: ProfileIdentityManager = db_manager.profile_identity
    thought_manager: ThoughtManager = db_manager.thought

    # --- 2. Get active identity (or set default) ---
    active_identity_res = profile_identity_manager.get_active_identity(current_user)
    if not active_identity_res.get("success", False):
        active_identity_res = profile_identity_manager.set_default_identity(current_user)
    if not active_identity_res.get("success", False):
        abort(500)
    
    active_identity: ProfileIdentity = active_identity_res.get("payload", {}).get("active_identity")

    # --- 3. Initialize Forms ---
    all_identities = current_user.identities
    create_thought_form = CreateThoughtForm()
    identity_choices = [(id.id, (id.custom_name if id.custom_name else id.template.name)) for id in all_identities]
    switch_identity_form = SwitchIdentityForm(identities=identity_choices)

    # --- 4. Handle POST Requests (Form Submissions) ---
    
    # Check if the "Create Thought" form was submitted
    if create_thought_form.submit_thought.data and create_thought_form.validate_on_submit():
        content = create_thought_form.create_thought.data
        db_res = thought_manager.create_thought(profile=current_user, profile_identity=active_identity, content=content)

        if not db_res.get("success", False):
            flash(message="Error creating thought...", category="error")

        return redirect(url_for('app.thoughts'))

    # Check if the "Switch Identity" form was submitted
    if switch_identity_form.submit_identity.data and switch_identity_form.validate_on_submit():
        identity_id = switch_identity_form.select_identity.data
        
        # Set the new identity
        active_identity_res = profile_identity_manager.set_identity(current_user, identity_id)

        if not active_identity_res.get("success", False):
            flash(message="Couldnt set identity...", category="error")
        else:
            active_identity = active_identity_res.get("payload", {}).get("active_identity")
            flash(message="Identity changed!", category="success")
        
        return redirect(url_for('app.thoughts'))

    # --- 5. Handle GET Request (Page Load) ---
    
    # --- 5a. Get data for the timeline filter ---
    thoughts: List[Thought] = active_identity.thoughts
    timeline_month_set = set()
    for thought in thoughts:
        timeline_month_set.add(
            (
                thought.created_at.year,
                thought.created_at.month,
                thought.created_at.strftime("%B") # Get month name
            )
        )
    
    # Sort the list of (year, month_num, month_name) tuples
    timeline_month_sorted = sorted(
        list(timeline_month_set),
        key=lambda x: (x[0], x[1]), # Sort by year, then month number
        reverse=True
    )

    # --- 5b. Get filtered thoughts for display ---
    filters = {
        "year": request.args.get("year", type=int),
        "month": request.args.get("month", type=int)
    }
    
    # This manager method defaults to "today" if no filters are passed
    ordered_thoughts_res = thought_manager.get_ordered_thoughts(active_identity.id, **filters)
    ordered_thoughts: List[Thought] = ordered_thoughts_res.get("payload", {}).get("thoughts", [])

    # --- 5c. Group thoughts by Day and Hour ---
    # This complex grouping logic is done here, not in the template,
    # to keep the template clean and simple.
    thought_groupings = {}
    for thought in ordered_thoughts:
        # Create a key for the day (e.g., "Saturday 8th November 2025")
        suffix = get_ordinal_suffix(thought.created_at.day)
        day_key = thought.created_at.strftime(f'%A %-d{suffix} %B %Y')
        
        # Create a key for the hour (e.g., "21:00")
        hour_key = thought.created_at.strftime('%H:00')
        
        # Create the final entry for the template
        new_entry = {
            "time": thought.created_at.strftime('%H:%M'),
            "thought_obj": thought
        }
        
        # Use setdefault to create the nested dicts/lists if they don't exist
        day_group = thought_groupings.setdefault(day_key, {})
        hour_group = day_group.setdefault(hour_key, [])
        hour_group.append(new_entry)

    # --- 6. Render the template ---
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