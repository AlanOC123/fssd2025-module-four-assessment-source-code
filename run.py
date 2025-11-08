"""
The main entry point for running the Flask application.

This script is responsible for:
1.  Reading the 'FLASK_CONFIG' environment variable to determine which
    configuration to use (e.g., 'testing', 'production').
2.  Calling the 'create_app' factory to build and configure the
    Flask application instance.
3.  (If run directly as a script) Starting the Flask development
    server on the port specified by the 'PORT' environment variable
    (defaulting to 8080).

You can run this file directly:
    $ python run.py

Or use the Flask CLI (which also uses this file):
    $ flask run
"""

import os
from app import create_app, db

# 1. Get the configuration key from the environment variables.
# This defaults to 'default' if FLASK_CONFIG is not set.
config_key = os.environ.get("FLASK_CONFIG", "default")

# 2. Create the Flask application instance
# This calls the factory function in app/__init__.py
app = create_app(config_key)

if __name__ == "__main__":
    """
    This block executes *only* when the script is run directly
    (e.g., 'python run.py') and not when it's imported by
    another module (like Gunicorn or the 'flask' command).
    
    This is the standard way to start a Flask development server.
    """
    # Get the port from the environment, defaulting to 8080 (common for dev)
    port_num = int(os.environ.get("PORT", 8080))
    
    # Run the app in debug mode.
    # debug=True enables the reloader and debugger.
    # This should NOT be used in production.

    is_debug_mode = os.environ.get("TESTING", False)

    app.run(debug=is_debug_mode, port=port_num)