from flask_wtf import FlaskForm
from flask_login import current_user
from flask_wtf.form import _Auto
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

    current_password_for_email = PasswordField(
        "Current Password",
        validators=[
            DataRequired("Enter your password...")
        ]
    )

    submit_email_change = SubmitField(
        "Save Changes"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        config = current_app.config
        is_testing = config.get("TESTING")

        check_email = (not is_testing)

        self.email.validators = list(self.email.validators)
        self.email.validators.append(
            Email("Enter a valid email address...", check_deliverability=check_email)
        )

    def validate_current_password_for_email(self, field):
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
            DataRequired("Enter your password...")
        ]
    )

    new_password = PasswordField(
        "New Password",
        validators=[
            DataRequired("Enter new password...")
        ]
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired("Confirm new password..."),
            EqualTo(fieldname="new_password", message="Passwords must match!")
        ]
    )

    submit_password_change = SubmitField(
        "Save Changes"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        config = current_app.config
        min_pw = config.get("PASSWORD_MIN_LENGTH", 8)
        max_pw = config.get("PASSWORD_MAX_LENGTH", 128)
        self.new_password.validators = list(self.new_password.validators)
        self.new_password.validators.append(
            Length(min=min_pw, max=max_pw, message=f"New password must between {min_pw} and {max_pw} characters.")
        )

    def validate_current_password(self, field):
        profile_manager: ProfileManager = current_app.db_manager.profile
        pw_validator_fn = profile_manager.pw_manager.verify

        attempted_password = field.data

        stored_hash = current_user.password

        if not pw_validator_fn(stored_hash, attempted_password):
            raise ValidationError("Incorrect password. Please try again")
        
    def validate_new_password(self, field):
        profile_manager: ProfileManager = current_app.db_manager.profile
        pw_validator = profile_manager.pw_manager
        
        attempted_password = field.data

        if not pw_validator.check_cap(attempted_password):
            raise ValidationError("New password must include a capital letter.")

        if not pw_validator.check_complexity(attempted_password):
            raise ValidationError("New password must include a symbol.")


class DeleteAccountForm(FlaskForm):
    deletion_confirmation_message = StringField(
        label="Type 'I understand this is a permanent deletion' to confirm",
        validators=[
            DataRequired("Please enter the message if you wish to continue...")
        ]
    )

    password_for_confirmation_deletion = PasswordField(
        label="Enter Password to Confirm Deletion",
        validators=[
            DataRequired("Please enter your password to confirm deletion")
        ]
    )

    submit_deletion_request = SubmitField(
        "Delete Account"
    )

    def validate_deletion_confirmation_message(self, field):
        input_msg = field.data.strip().lower()

        matches = input_msg == "I understand this is a permanent deletion".strip().lower()

        if not matches:
            raise ValidationError("Type the required message to confirm")

    def validate_password_for_confirmation_deletion(self, field):
        profile_manager: ProfileManager = current_app.db_manager.profile
        pw_validator_fn = profile_manager.pw_manager.verify

        attempted_password = field.data

        stored_hash = current_user.password

        if not pw_validator_fn(stored_hash, attempted_password):
            raise ValidationError("Incorrect password. Please try again")

class UpdateThemeForm(FlaskForm):
    pass

class UpdateIdentitiesForm(FlaskForm):
    pass