"""
Defines the WTForms classes for the 'settings' blueprint.

This file contains all the forms used on the user settings pages.
It includes forms with:
- Dynamic validators added in __init__ (based on app config).
- Custom inline validators (e.g., for checking current password).
- Dynamically populated choices (e.g., for theme selection).
- FieldList for managing a dynamic list of sub-forms (for identities).
"""

from flask_wtf import FlaskForm, Form
from flask_login import current_user
from flask_wtf.form import _Auto
from wtforms import (
    StringField, EmailField, PasswordField, BooleanField, SubmitField, 
    DateField, RadioField, HiddenField, FieldList, FormField
)
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from flask import current_app
from app.helper.classes.database.ProfileManager import ProfileManager
from app.database.models import ThemeMode

class UpdateProfileForm(FlaskForm):
    """
    Form for updating the user's personal (non-account) details.
    
    Fields:
        - first_name
        - surname
        - date_of_birth
    """
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
    """
    Form for updating the user's email address.
    
    Requires the user to re-enter their current password for security.
    
    Custom Validator:
        - validate_current_password_for_email: Confirms the password is correct.
    """
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
        """
        Initializes the UpdateEmailForm.
        
        Dynamically adds an Email validator, disabling the 'check_deliverability'
        flag during testing to speed up tests and avoid network calls.
        """
        super().__init__(*args, **kwargs)
        config = current_app.config
        is_testing = config.get("TESTING")
        check_email = (not is_testing)

        # Dynamically append the Email validator to the 'email' field
        self.email.validators.append(
            Email("Enter a valid email address...", check_deliverability=check_email)
        )

    def validate_current_password_for_email(self, field):
        """
        Custom inline validator for the 'current_password_for_email' field.
        
        Checks the provided password against the 'current_user's'
        stored password hash.
        
        Args:
            field: The 'current_password_for_email' field object.
            
        Raises:
            ValidationError: If the password does not match.
        """
        profile_manager: ProfileManager = current_app.db_manager.profile
        pw_validator_fn = profile_manager.pw_manager.verify
        attempted_password = field.data
        stored_hash = current_user.password

        if not pw_validator_fn(stored_hash, attempted_password):
            raise ValidationError("Incorrect password. Please try again")

class UpdatePasswordForm(FlaskForm):
    """
    Form for changing the user's password.
    
    Requires the user's current password and confirmation of the new one.
    
    Custom Validators:
        - validate_current_password: Confirms the current password is correct.
        - validate_new_password: Checks complexity rules for the new password.
    """
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
        """
        Initializes the UpdatePasswordForm.
        
        Dynamically adds 'Length' validators to the password fields
        based on the 'PASSWORD_MIN_LENGTH' and 'PASSWORD_MAX_LENGTH'
        settings in the Flask app config.
        """
        super().__init__(*args, **kwargs)
        config = current_app.config
        min_pw = config.get("PASSWORD_MIN_LENGTH", 8)
        max_pw = config.get("PASSWORD_MAX_LENGTH", 128)
        
        # Dynamically append the Length validator
        self.new_password.validators.append(
            Length(min=min_pw, max=max_pw, message=f"New password must between {min_pw} and {max_pw} characters.")
        )

    def validate_current_password(self, field):
        """
        Custom inline validator for the 'current_password' field.
        
        Checks the provided password against the 'current_user's'
        stored password hash.
        
        Args:
            field: The 'current_password' field object.
            
        Raises:
            ValidationError: If the password does not match.
        """
        profile_manager: ProfileManager = current_app.db_manager.profile
        pw_validator_fn = profile_manager.pw_manager.verify
        attempted_password = field.data
        stored_hash = current_user.password

        if not pw_validator_fn(stored_hash, attempted_password):
            raise ValidationError("Incorrect password. Please try again")
        
    def validate_new_password(self, field):
        """
        Custom inline validator for the 'new_password' field.
        
        Checks the new password against the app's complexity rules
        (e.g., must contain a capital, must contain a symbol)
        using the PasswordManager.
        
        Args:
            field: The 'new_password' field object.
            
        Raises:
            ValidationError: If the new password fails a complexity check.
        """
        profile_manager: ProfileManager = current_app.db_manager.profile
        pw_validator = profile_manager.pw_manager
        attempted_password = field.data

        if not pw_validator.check_cap(attempted_password):
            raise ValidationError("New password must include a capital letter.")

        if not pw_validator.check_complexity(attempted_password):
            raise ValidationError("New password must include a symbol.")

class DeleteAccountForm(FlaskForm):
    """
    Form for handling the permanent deletion of a user's account.
    
    Includes two checks:
    1. A confirmation string must be typed exactly.
    2. The user's current password must be entered correctly.
    
    Custom Validators:
        - validate_deletion_confirmation_message
        - validate_password_for_confirmation_deletion
    """
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
        """
        Custom inline validator for the confirmation message.
        
        Checks that the user typed the exact confirmation phrase.
        
        Args:
            field: The 'deletion_confirmation_message' field object.
            
        Raises:
            ValidationError: If the string does not match.
        """
        input_msg = field.data.strip().lower()
        required_msg = "i understand this is a permanent deletion"
        
        if input_msg != required_msg:
            raise ValidationError("Type the required message to confirm")

    def validate_password_for_confirmation_deletion(self, field):
        """
        Custom inline validator for the password confirmation.
        
        Checks the provided password against the 'current_user's'
        stored password hash.
        
        Args:
            field: The 'password_for_confirmation_deletion' field object.
            
        Raises:
            ValidationError: If the password does not match.
        """
        profile_manager: ProfileManager = current_app.db_manager.profile
        pw_validator_fn = profile_manager.pw_manager.verify
        attempted_password = field.data
        stored_hash = current_user.password

        if not pw_validator_fn(stored_hash, attempted_password):
            raise ValidationError("Incorrect password. Please try again")

class UpdateThemeColorSchemeForm(FlaskForm):
    """
    Form for updating the user's color scheme.
    
    The choices for this form (e.g., "Default", "Ocean Blue") are
    dynamically populated from the database in the 'appearance' route.
    """
    theme_id = RadioField(
        "Select Theme",
        coerce=int, # Coerces the form value from string to int
        validators=[
            DataRequired("Please select an option...")
        ]
    )
    submit_scheme = SubmitField("Save Scheme")

    def __init__(self, *args, **kwargs):
        """
        Initializes the form and dynamically sets the theme choices.
        
        Args:
            *args: Standard FlaskForm arguments.
            **kwargs: Expects 'theme_choices' (a list of (id, name) tuples)
                      to be passed in from the route.
        """
        # Pop 'theme_choices' from kwargs before calling super()
        theme_choice_list = kwargs.pop("theme_choices", [])
        super().__init__(*args, **kwargs)
        
        # Set the 'choices' for the RadioField
        self.theme_id.choices = theme_choice_list

class UpdateThemeModeForm(FlaskForm):
    """
    Form for updating the user's theme mode (Light/Dark/System).
    
    The choices for this form are dynamically populated from
    the ThemeMode enum in the 'appearance' route.
    """
    theme_mode = RadioField(
        "Select Mode",
        coerce=ThemeMode, # Coerces the string value (e.g., 'dark')
                         # back into a ThemeMode enum object.
        validators=[
            DataRequired("Select a theme mode...")
        ]
    )
    submit_mode = SubmitField("Save Mode")

    def __init__(self, *args, **kwargs):
        """
        Initializes the form and dynamically sets the theme mode choices.
        
        Args:
            *args: Standard FlaskForm arguments.
            **kwargs: Expects 'theme_modes' (a list of (value, name) tuples
                      from the ThemeMode enum) to be passed in from the route.
        """
        theme_modes = kwargs.pop("theme_modes", [])
        super().__init__(*args, **kwargs)
        self.theme_mode.choices = theme_modes

class EditIdentityEntryForm(Form):
    """
    This is a sub-form, not a full FlaskForm.
    
    It represents a *single entry* in the list of identities on the
    'Identities' settings page. It is used by UpdateIdentitiesForm
    in a FieldList.
    """
    identity_id = HiddenField() # Stores the ID of the identity
    identity_custom_name = StringField(
        "Custom Name",
        validators=[
            DataRequired(),
            Length(min=2, max=50, message="Name must be between 2 and 50 characters...")
        ]
    )

class UpdateIdentitiesForm(FlaskForm):
    """
    The main form for the 'Identities' settings page.
    
    This form uses a FieldList to manage a dynamic list of
    'EditIdentityEntryForm' sub-forms, one for each identity
    the user possesses.
    """
    identities = FieldList(FormField(EditIdentityEntryForm))
    submit = SubmitField(" Save Changes")