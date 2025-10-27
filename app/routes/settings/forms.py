from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, EmailField, PasswordField, BooleanField, SubmitField, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from flask import current_app
from app.helper.classes.database.ProfileManager import ProfileManager

class UpdateProfileForm(FlaskForm):
    first_name = StringField(
        "First Name",
        validators=[
            DataRequired("Enter your first name...")
        ]
    )

    surname = StringField(
        "Last Name",
        validators=[
            DataRequired("Enter your last name...")
        ]
    )

    date_of_birth = DateField(
        "Date of Birth",
        validators=[
            DataRequired("Enter your date of birth...")
        ]
    )

    submit = SubmitField(
        "Save Changes"
    )

class UpdateEmailForm(FlaskForm):
    email = EmailField(
        "Email",
        validators=[
            DataRequired("Enter your email...")
        ]
    )

    current_password = PasswordField(
        "Current Password",
        validators=[
            DataRequired("Enter your password...")
        ]
    )

    submit = SubmitField(
        "Save Changes"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        config = current_app.config
        is_testing = config.get("TESTING")

        check_email = (not is_testing)

        self.email.validators.append(
            Email("Enter a valid email address...", check_deliverability=check_email)
        )

    def validate_current_password(self, field):
        profile_manager: ProfileManager = current_app.db_manager.profile
        pw_validator_fn = profile_manager.pw_manager.verify

        attempted_password = field.data

        stored_hash = current_user.password

        if not pw_validator_fn(stored_hash, attempted_password):
            raise ValidationError("Incorrect password. Please try again")



class UpdatePasswordForm(FlaskForm):
    current_password = PasswordField(
        "Current Password",
        validators=[
            DataRequired("Enter your password")
        ]
    )

class DeleteAccountForm(FlaskForm):
    pass

class UpdateThemeForm(FlaskForm):
    pass

class UpdateIdentitiesForm(FlaskForm):
    pass