"""
Defines the WTForms classes for the main application blueprint ('app').

This file contains all forms used by the 'main' routes (routes.py), including:
- Creating new thoughts, projects, and tasks.
- Switching the active identity or project.
"""

from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, RadioField, StringField, DateField
from wtforms.validators import DataRequired, Length, Optional
from datetime import date, timedelta
from app.database.models import Difficulty

class CreateThoughtForm(FlaskForm):
    """
    Form for creating a new thought on the Thoughts page.
    
    The label for 'create_thought' is intentionally blank ("") as the
    template provides a 'placeholder' and other contextual elements.
    """
    create_thought = TextAreaField(
        "",
        validators=[
            DataRequired("Enter some content..."),
            Length(min=5, max=200, message="Thoughts must be between 5 and 200 characters long...")
        ]
    )
    submit_thought = SubmitField("Submit")

class SwitchIdentityForm(FlaskForm):
    """
    Form for switching the active identity.
    
    This form is used on multiple pages (Projects, Tasks, Thoughts) inside
    a sidebar or menu. The choices for the 'select_identity' field
    are dynamically populated in the route by passing a list to the constructor.
    """
    select_identity = RadioField(
        "", # Label is provided by the template.
        coerce=int, # Coerces the selected value from a string to an integer.
        validators=[
            DataRequired("Please select an option...")
        ]
    )
    submit_identity = SubmitField("Submit")

    def __init__(self, *args, **kwargs):
        """
        Initializes the form and dynamically sets the identity choices.
        
        Args:
            *args: Standard FlaskForm arguments.
            **kwargs: Expects 'identities' (a list of (id, name) tuples)
                      to be passed in from the route.
        """
        # Pop 'identities' from kwargs *before* calling super().__init__
        # so that FlaskForm doesn't try to use it as form data.
        identities = kwargs.pop("identities", [])
        super().__init__(*args, **kwargs)
        
        # Set the 'choices' for the RadioField
        self.select_identity.choices = identities

class CreateProjectForm(FlaskForm):
    """Form for creating a new project in the 'Projects' page sidebar."""
    project_name = StringField(
        label="Project Name",
        validators=[
            DataRequired("Enter a project name..."),
            Length(min=5, max=100, message="Project Name must between 5 and 100 characters long...")
        ]
    )

    project_description = TextAreaField(
        label="Project Description",
        validators=[Optional()] # This field is allowed to be empty.
    )

    project_start_date = DateField(
        label="Start Date",
        validators=[
            DataRequired("Enter a start date")
        ],
        default=date.today() # Defaults to the current date.
    )

    project_end_date = DateField(
        label="End Date",
        validators=[
            DataRequired("Enter an end date"),
        ],
        default=timedelta(days=30) + date.today() # Defaults to 30 days from now.
    )

    submit_project = SubmitField("Create Project")
    
class CreateTaskForm(FlaskForm):
    """Form for creating a new task in the 'Tasks' page sidebar."""
    task_name = StringField(
        label="Task Name",
        validators=[
            DataRequired("Enter a task name..."),
            Length(min=5, max=100, message="Task Name must between 5 and 100 characters long...")
        ]
    )

    task_due_date = DateField(
        label="Due Date",
        validators=[
            DataRequired("Enter a start date")
        ],
        default=timedelta(days=30) + date.today()
    )

    task_difficulty = RadioField(
        label="Difficulty",
        coerce=Difficulty, # Coerces the string value back to a Difficulty enum.
        validators=[
            DataRequired()
        ],
        default=Difficulty.MEDIUM.value
    )

    submit_task = SubmitField("Submit")

    def __init__(self, *args, **kwargs):
        """
        Initializes the form and dynamically sets the difficulty choices.
        
        Args:
            *args: Standard FlaskForm arguments.
            **kwargs: Expects 'difficulty_choices' (a list of (value, name)
                      tuples from the Difficulty enum).
        """
        difficulty_choices = kwargs.pop("difficulty_choices", [])
        super().__init__(*args, **kwargs)
        self.task_difficulty.choices = difficulty_choices

class SwitchProjectForm(FlaskForm):
    """
    Form for switching the active project on the 'Tasks' page.
    
    The choices for this form are dynamically populated from the
    user's projects in the route.
    """
    switch_project = RadioField(
        label="", # Label is provided by the template.
        coerce=int, # Coerces the selected value from a string to an integer.
        validators=[
            DataRequired()
        ]
    )

    submit_project_switch = SubmitField("Switch")

    def __init__(self, *args, **kwargs):
        """
        Initializes the form and dynamically sets the project choices.
        
        Args:
            *args: Standard FlaskForm arguments.
            **kwargs: Expects 'project_choices' (a list of (id, name)
                      tuples) to be passed in from the route.
        """
        project_choices = kwargs.pop("project_choices", [])
        super().__init__(*args, **kwargs)
        self.switch_project.choices = project_choices