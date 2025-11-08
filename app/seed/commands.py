"""
Defines custom Flask CLI commands for database management.

This file provides two essential commands for development and deployment:
1.  'flask seed-db': Seeds the database with initial data (themes, identities,
    and a test user for testing environments).
2.  'flask reset-db': Destructively drops all data, recreates the schema
    from the models, and then runs the seed-db command.

These commands are registered with the Flask app in app/__init__.py.
"""

import click
from flask import current_app
from flask.cli import with_appcontext
import json
from ..extensions import db
from pathlib import Path
from functools import lru_cache

# Define paths to the JSON data files, relative to this file's location
__IDENTITY_DATA_PATH__ = Path(__file__).with_name("identities.json")
__THEMES_DATA_PATH__ = Path(__file__).with_name("themes.json")

def get_seed_data(path: Path) -> dict:
    """
    A helper function to read and parse a JSON seed file.

    Args:
        path (Path): A pathlib.Path object pointing to the JSON file.

    Raises:
        RuntimeError: If the file is not found or contains invalid JSON.

    Returns:
        dict: The parsed JSON data.
    """
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as e:
        raise RuntimeError(f"Missing data file: {path}") from e
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON in {path}") from e
    
@lru_cache(maxsize=1)
def _load_identities() -> dict:
    """
    Cached helper to load the identities.json file.
    
    '@lru_cache(maxsize=1)' ensures this file is read from disk
    only once, even if called multiple times.
    """
    return get_seed_data(__IDENTITY_DATA_PATH__)

@lru_cache(maxsize=1)
def _load_themes() -> dict:
    """
    Cached helper to load the themes.json file.
    
    '@lru_cache(maxsize=1)' ensures this file is read from disk
    only once, even if called multiple times.
    """
    return get_seed_data(__THEMES_DATA_PATH__)

def seed_profile():
    """
    Seeds a test user *only* if the app is in 'TESTING' mode.
    
    This function checks the 'TESTING' config flag. If True, it
    seeds the test user defined in 'config.py'. It also checks
    for duplicates to avoid errors on repeated runs.
    """
    # Get the current app
    is_test = current_app.config.get("TESTING")

    # This is a safety check to prevent seeding test users in production
    if not is_test:
        click.echo("Skipping test profile seed (app not in TESTING mode).")
        return
    
    click.echo("Seeding test profile data...")
    
    test_user = current_app.config.get("TEST_USER")

    # BUG FIX: Corrected typo "Chceking" -> "Checking"
    click.echo("Checking if test profile exists...")

    # Check for duplicates
    db_res = current_app.db_manager.profile.get_profile_by_email(email=test_user["email"])

    if db_res.get("success"):
        click.echo("Test profile already created...")
        return

    click.echo("Creating profile...")
    db_res = current_app.db_manager.profile.create_profile(**test_user)

    if not db_res.get("success"):
        click.echo(f"Failed to create test profile: {db_res.get('msg')}")
        return

    click.echo("Test profile created...")

def seed_identities():
    """
    Seeds the 'identity_templates' table from 'identities.json'.
    
    This function is idempotent: it checks the database for existing
    identities by name and only seeds new ones that are not
    already present.
    """
    click.echo("Loading identities data...")
    identities_data = _load_identities() # From JSON file

    # Get all identity templates *currently* in the database
    # BUG FIX: The payload key is 'identity_templates' (plural)
    curr_identities_list = current_app.db_manager.identity_template.get_all().get("payload", {}).get("identity_templates", [])
    curr_identities = set(identity.name for identity in curr_identities_list)

    # Get all identity names from the JSON file
    new_identities = set(identity.get("name") for identity in identities_data)

    # Find which identities are in the JSON but not in the DB
    difference = new_identities.difference(curr_identities)

    if len(difference) == 0:
        click.echo("No new identities to seed.")
        return
    
    # Filter the data to only include the new, missing identities
    identities_to_seed = [
        identity for identity in identities_data if identity.get("name") in difference
    ]
    
    click.echo(f"Found {len(identities_to_seed)} new identities. Starting seed...")
    res = current_app.db_manager.identity_template.init(identities_to_seed)

    if not res.get("success"):
        click.echo(f"Failed to initialise identities. Error: {res.get('msg')}")
    else:
        click.echo(f"Identities created successfully.")

def seed_themes():
    """
    Seeds the 'themes' table from 'themes.json'.
    
    This function is idempotent: it checks the database for existing
    themes by name and only seeds new ones that are not
    already present.
    """
    themes_data = _load_themes() # From JSON file

    # Get all themes *currently* in the database
    # BUG FIX: The payload key is 'themes' (plural), not 'theme'
    curr_themes_list = current_app.db_manager.theme.get_all().get("payload", {}).get("themes", [])
    curr_themes = set(theme.name for theme in curr_themes_list)

    # Get all theme names from the JSON file
    new_themes = set(theme.get("name") for theme in themes_data)

    # Find which themes are in the JSON but not in the DB
    difference = new_themes.difference(curr_themes)

    if len(difference) == 0:
        click.echo("No new themes to seed.")
        return

    # Filter the data to only include the new, missing themes
    themes_to_seed = [
        theme for theme in themes_data if theme.get("name") in difference
    ]

    click.echo(f"Found {len(themes_to_seed)} new themes. Starting seed...")
    res = current_app.db_manager.theme.init(themes_to_seed)

    if not res.get("success"):
        click.echo(f"Failed to initialise themes. Error: {res.get('msg')}")
    else:
        click.echo(f"Themes created successfully.")

def seed_database():
    """
    Main orchestrator function for seeding.
    
    Calls the individual seeders in the correct order.
    """
    click.echo("Seeding initial data...")
    seed_identities()
    seed_themes()
    seed_profile() # Seed profile last, as it depends on themes

def register_commands(app):
    """
    Registers all CLI commands with the Flask app instance.
    
    This function is called by the app factory (create_app).

    Args:
        app (Flask): The Flask application instance.
    """
    
    @app.cli.command("seed-db")
    @with_appcontext
    def seed_db_command():
        """
        Flask CLI command: 'flask seed-db'
        
        Seeds the database with initial data (themes, identities, test user).
        This command is idempotent and safe to run multiple times.
        """
        seed_database()

    @app.cli.command('reset-db')
    @with_appcontext
    def reset_table():
        """
        Flask CLI command: 'flask reset-db'
        
        Destroys and recreates the entire database.
        
        1. Drops ALL tables and data.
        2. Re-creates all tables based on the current models.py
           (NOTE: This bypasses migration history).
        3. Calls 'seed-db' to add initial data.
        
        This is for development use only.
        """
        # Ask for confirmation before destroying data
        click.confirm("This will delete all data in the database. Are you sure?", abort=True)
        
        # Drop Existing DB Tables
        click.echo("Dropping all database tables...")
        db.drop_all()

        # Recreate them
        click.echo("Recreating database tables...")
        db.create_all()
        click.echo("Tables created successfully")

        # Re-seed the fresh database
        seed_database()