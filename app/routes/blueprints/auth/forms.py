from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, BooleanField, SubmitField, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class LoginForm(FlaskForm):
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
        super().__init__(*args, **kwargs)

        from flask import current_app
        config = current_app.config

        min_pw: int = config.get("PASSWORD_MIN_LENGTH", 8)
        max_pw: int = config.get("PASSWORD_MAX_LENGTH", 128)

        is_testing_env = config.get("TESTING", False)
        check_email = (not is_testing_env)

        self.password.validators.append(
            Length(min=min_pw, max=max_pw, message=f"Password must be {min_pw} characters long...")
        )

        self.email.validators.append(
            Email("Please enter a valid email...", check_deliverability=check_email),
        )

class RegisterForm(FlaskForm):
    first_name = StringField(
        "First Name",
        validators=[
            DataRequired("Please enter your first name...")
        ]
    )

    last_name = StringField(
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
            DataRequired(message="Please enter your password..."),
            EqualTo("password", message="Passwords don't match...")
        ]
    )

    submit = SubmitField("Register")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        from flask import current_app
        config = current_app.config

        min_pw: int = config.get("PASSWORD_MIN_LENGTH", 8)
        max_pw: int = config.get("PASSWORD_MAX_LENGTH", 128)

        is_testing_env = config.get("TESTING", False)
        check_email = (not is_testing_env)

        msg = f"Password must be between {min_pw} and {max_pw} characters long..."

        self.password.validators.append(
            Length(min=min_pw, max=max_pw, message=msg)
        )

        self.confirm_password.validators.append(
            Length(min=min_pw, max=max_pw, message=msg)
        )

        self.email.validators.append(
            Email("Please enter a valid email...", check_deliverability=check_email),
        )