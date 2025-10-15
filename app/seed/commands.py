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
        click.echo(f"Error creating profile {db_res.get("msg")}")

    print(db_res.get("payload").get("profile").identities[0].template.name)
    
    click.echo("Test profile created")

def seed_identities():
    click.echo("Loading identities data...")
    identities_data = _load_identities()
    
    click.echo("Identities data loaded. Seeding data...")
    for identity_info in identities_data:
        exists = current_app.db_manager.identity_template.get_by_name(identity_info["name"]).get("success")

        if not exists:
            click.echo(f"New identity found. Adding to table. '{identity_info['name']}'")
            current_app.db_manager.identity_template.create(**identity_info)
            click.echo(f"- Added identity: '{identity_info['name']}'")
        else:
            click.echo(f"Existing identity found '{identity_info['name']}'")

def seed_themes():
    click.echo("Loading themes data...")
    identities_data = _load_themes()
    
    click.echo("Themes data loaded. Seeding data...")
    for theme_raw in identities_data:
        db_res = current_app.db_manager.theme.get_theme_by_name(theme_raw["name"])

        if not db_res.get("success"):
            click.echo(f"New theme found. Adding to table. '{theme_raw['name']}'")
            current_app.db_manager.theme.create_theme(**theme_raw)
            click.echo(f"- Added theme: '{theme_raw['name']}'")
        else:
            click.echo(f"Existing theme found '{theme_raw['name']}'")

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