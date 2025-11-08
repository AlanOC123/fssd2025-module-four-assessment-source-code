import click
from flask import current_app
from flask.cli import with_appcontext
import json
from ..extensions import db
from pathlib import Path
from functools import lru_cache

__IDENTITY_DATA_PATH__ = Path(__file__).with_name("identities.json")
__THEMES_DATA_PATH__ = Path(__file__).with_name("themes.json")

def get_seed_data(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as e:
        raise RuntimeError(f"Missing data file: {path}") from e
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON in {path}") from e
    
@lru_cache(maxsize=1)
def _load_identities():
    return get_seed_data(__IDENTITY_DATA_PATH__)

@lru_cache(maxsize=1)
def _load_themes():
    return get_seed_data(__THEMES_DATA_PATH__)

def seed_profile():
    # Get the current app
    is_test = current_app.config.get("TESTING")

    if not is_test:
        return
    
    click.echo("Seeding test profile data...")
    
    test_user = current_app.config.get("TEST_USER")

    click.echo("Chceking test profile exists...")

    # Check for duplicates
    db_res = current_app.db_manager.profile.get_profile_by_email(email=test_user["email"])

    if db_res.get("success"):
        print("Test profile already created...")
        return

    click.echo("Creating profile...")
    db_res = current_app.db_manager.profile.create_profile(**test_user)

    if not db_res.get("success"):
        click.echo(f"{db_res.get("msg")}")
        return

    click.echo("Test profile created...")

def seed_identities():
    click.echo("Loading identities data...")
    # Load the identities
    identities_data = _load_identities()

    # Get the current ones in a set
    curr_identities = set(
        identity.name for identity in current_app.db_manager.identity_template.get_all().get("payload", {}).get("identity_templates", [])
    )

    # Get the names of the new ones
    new_identities = set(identity.get("name") for identity in identities_data)

    # Check the difference between current and new
    difference = new_identities.difference(curr_identities)

    if len(difference) == 0:
        click.echo("No new identities to seed...")
        return
    
    click.echo("Identities data loaded. Starting seed...")
    res = current_app.db_manager.identity_template.init(identities_data)

    if not res.get("success"):
        click.echo(f"Failed to initialise identities. Error: {res.get("msg")}")
    else:
        click.echo(f"Identities created: {res.get("payload", {}).get("templates", [])}")

def seed_themes():
    themes_data = _load_themes()

    # Get the current ones in a set
    curr_themes = set(
        theme.name for theme in current_app.db_manager.theme.get_all().get("payload", {}).get("themes", [])
    )

    # Get the names of the new ones
    new_themes = set(theme.get("name") for theme in themes_data)

    # Check the difference between current and new
    difference = new_themes.difference(curr_themes)

    if len(difference) == 0:
        click.echo("No new themes to seed...")
        return

    res = current_app.db_manager.theme.init(themes_data)

    if not res.get("success"):
        click.echo(f"Failed to initialise themes. Error: {res.get("msg")}")
    else:
        click.echo(f"Themes created: {res.get("payload", {}).get("themes", [])}")

def seed_database():
    click.echo("Seeding initial data...")
    seed_identities()
    seed_themes()
    seed_profile()

def register_commands(app):
    @app.cli.command("seed-db")
    @with_appcontext
    def seed_db_command():
        seed_database()

    @app.cli.command('reset-db')
    @with_appcontext
    def reset_table():
        click.confirm("This will delete all data in the database. Are you sure?", abort=True)
        # Drop Existing DB Tables
        click.echo("Dropping all database tables...")
        db.drop_all()

        # Recreate them
        click.echo("Recreating database tables...")
        db.create_all()
        click.echo("Tables created successfully")

        seed_database()