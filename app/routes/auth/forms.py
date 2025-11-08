"""
Defines the WTForms classes for user authentication (Login and Register).

This file contains the forms used in the 'auth' blueprint. These forms
include standard validators (DataRequired, Length) as well as custom
inline validators (validate_password, validate_email) that check
business logic against the database and app configuration.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, BooleanField, SubmitField, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.helper.classes.database.ProfileManager import ProfileManager
from flask import current_app

class LoginForm(FlaskForm):
    """
    Form for handling user login.
    
    Fields:
        - email
        - password
        - remember_me (Checkbox)
    """
    email = EmailField(
        "Email",
        validators=[
            DataRequired(message="Please enter your email..."),
        ]
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Please enter your password..."),
        ]
    )

    remember_me = BooleanField("")

    submit = SubmitField("Sign In")

    def __init__(self, *args, **kwargs):
        """
        Initializes the LoginForm and dynamically adds config-based validators.
        
        This constructor pulls password length rules from the app config
        and adds the appropriate validators to the fields. It also disables
        the 'check_deliverability' email validator in testing environments
        to speed up tests and avoid network calls.
        """
        super().__init__(*args, **kwargs)

        # Get the app config
        from flask import current_app
        config = current_app.config

        # Get password length rules
        min_pw: int = config.get("PASSWORD_MIN_LENGTH", 8)
        max_pw: int = config.get("PASSWORD_MAX_LENGTH", 128)

        # Disable email deliverability check in testing (it's slow)
        is_testing_env = config.get("TESTING", False)
        check_email = (not is_testing_env)

        # Dynamically add the length validator to the password field
        self.password.validators.append(
            Length(min=min_pw, max=max_pw, message=f"Password must be {min_pw} characters long...")
        )

        # Dynamically add the email validator
        self.email.validators.append(
            Email("Please enter a valid email...", check_deliverability=check_email),
        )

class RegisterForm(FlaskForm):
    """
    Form for handling new user registration.

    Fields:
        - first_name
        - surname
        - dob (Date of Birth)
        - email
        - password
        - confirm_password
    
    Custom Validators:
        - validate_password: Checks password complexity (caps, symbols).
        - validate_email: Checks for duplicate emails in the database.
    """
    first_name = StringField(
        "First Name",
        validators=[
            DataRequired("Please enter your first name...")
        ]
    )

    surname = StringField(
        "Last Name",
        validators=[
            DataRequired("Please enter your last name...")
        ]
    )

    dob = DateField(
        "Date of Birth",
        validators=[
            DataRequired("Please enter your date of birth...")
        ]
    )

    email = EmailField(
        "Email",
        validators=[
            DataRequired(message="Please enter your email..."),
            Email(message="Please enter a valid email...")
        ]
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Please enter your password..."),
        ]
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(message="Please confirm your password..."),
            EqualTo("password", message="Passwords don't match...")
        ]
    )

    submit = SubmitField("Register")

    def __init__(self, *args, **kwargs):
        """
        Initializes the RegisterForm and dynamically adds config-based validators.
        
        This constructor pulls password length rules from the app config
        and adds the appropriate validators to the fields. It also disables
        the 'check_deliverability' email validator in testing environments.
        """
        super().__init__(*args, **kwargs)

        # Get the app config
        from flask import current_app
        config = current_app.config

        # Get password length rules
        min_pw: int = config.get("PASSWORD_MIN_LENGTH", 8)
        max_pw: int = config.get("PASSWORD_MAX_LENGTH", 128)

        # Disable email deliverability check in testing
        is_testing_env = config.get("TESTING", False)
        check_email = (not is_testing_env)

        msg = f"Password must be between {min_pw} and {max_pw} characters long..."

        # Dynamically add the length validator to the password fields
        self.password.validators.append(
            Length(min=min_pw, max=max_pw, message=msg)
        )
        self.confirm_password.validators.append(
            Length(min=min_pw, max=max_pw, message=msg)
        )

        # Dynamically add the email validator
        self.email.validators.append(
            Email("Please enter a valid email...", check_deliverability=check_email),
        )
    
    def validate_password(self, field):
        """
        Custom inline validator for the 'password' field.
        
        This is automatically called by WTForms during validation.
        It checks the password against the complexity rules
        (capital letter, symbol) defined in the PasswordManager.
        
        Args:
            field: The 'password' field object.
            
        Raises:
            ValidationError: If the password fails a complexity check.
        """
        attempted_password = field.data

        # Get the password validator from the ProfileManager
        profile_manager: ProfileManager = current_app.db_manager.profile
        pw_validator = profile_manager.pw_manager

        # Check for capital letter
        if not pw_validator.check_cap(attempted_password):
            raise ValidationError("New password must include a capital letter.")

        # Check for symbol
        if not pw_validator.check_complexity(attempted_password):
            raise ValidationError("New password must include a symbol.")
        
    def validate_email(self, field):
        """
        Custom inline validator for the 'email' field.
        
        This is automatically called by WTForms during validation.
        It checks if the email already exists in the database to prevent
        duplicate user accounts.
        
        Args:
            field: The 'email' field object.
            
        Raises:
            ValidationError: If the email is already taken.
        """
        email = field.data.strip()

        # Get the ProfileManager
        profile_manager: ProfileManager = current_app.db_manager.profile

        # Check if a profile with this email already exists
        is_duplicate = profile_manager.get_profile_by_email(email=email).get("success", False) # Note: Changed default to False

        if is_duplicate:
            # If 'success' is True, it means a profile was found
            raise ValidationError("An account with this email address already exists.")