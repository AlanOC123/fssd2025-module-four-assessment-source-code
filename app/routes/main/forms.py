from flask_wtf import FlaskForm
from flask_wtf.form import _Auto
from wtforms import TextAreaField, SubmitField, RadioField
from wtforms.validators import DataRequired, Length

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
