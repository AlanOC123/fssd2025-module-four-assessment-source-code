from flask_wtf import FlaskForm
from flask_wtf.form import _Auto
from wtforms import TextAreaField, SubmitField, RadioField, StringField, DateField
from wtforms.validators import DataRequired, Length, Optional
from datetime import date, timedelta
from app.database.models import Status

class CreateThoughtForm(FlaskForm):
    create_thought = TextAreaField(
        "",
        validators=[
            DataRequired("Enter some content..."),
            Length(min=5, max=200, message="Thoughts must be between 5 and 200 characters long...")
        ]
    )

    submit_thought = SubmitField("Submit")

class SwitchIdentityForm(FlaskForm):
    select_identity = RadioField(
        "",
        coerce=int,
        validators=[
            DataRequired("Please select an option...")
        ]
    )

    submit_identity = SubmitField("Submit")

    def __init__(self, *args, **kwargs):
        identities = kwargs.pop("identities", [])
        super().__init__(*args, **kwargs)
        self.select_identity.choices = identities

class CreateProjectForm(FlaskForm):
    project_name = StringField(
        label="Project Name",
        validators=[
            DataRequired("Enter a project name..."),
            Length(min=5, max=100, message="Project Name must between 5 and 100 characters long...")
        ]
    )

    project_description = TextAreaField(
        label="Project Description",
        validators=[Optional()]
    )

    project_start_date = DateField(
        label="Start Date",
        validators=[
            DataRequired("Enter a start date")
        ],
        default=date.today()
    )

    project_end_date = DateField(
        label="End Date",
        validators=[
            DataRequired("Enter an end date"),
        ],
        default=timedelta(days=30) + date.today()
    )

    project_status = RadioField(
        label="Project Status",
        coerce=Status,
        default=Status.NOT_STARTED.value
    )

    submit_project = SubmitField("Create Project")

    def __init__(self, *args, **kwargs):
        status_choices = kwargs.pop("status", [])
        super().__init__(*args, **kwargs)

        self.project_status.choices = status_choices
