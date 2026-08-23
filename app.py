"""
BactoAI - AI-powered antibiotic resistance prediction from whole genome sequences.

This is the legacy entry point. The application has been restructured into a
modular package under `bactoai/`. This file is kept for backward compatibility
with existing deployments (Procfile, Docker, etc.).

For new development, use `run.py` or the `bactoai` package directly.
"""

# Import the application factory from the new package
from bactoai.app import create_app
from bactoai.config import config_map
import os

# Determine environment
env = os.environ.get("FLASK_ENV", "development")
config_class = config_map.get(env, config_map["development"])

# Create the Flask app (used by Gunicorn, Docker, etc.)
app = create_app(config_class=config_class)


# =====================================================================
# CLI Commands (preserved from original)
# =====================================================================

@app.cli.command("create-user")
def create_user_cli():
    """Create a new user: flask create-user"""
    import click
    from bactoai.database import create_user

    username = click.prompt("Username")
    password = click.prompt("Password", hide_input=True, confirmation_prompt=True)
    clinic = click.prompt("Clinic name (optional)", default="")
    role = click.prompt("Role (admin/lab_tech/viewer)", default="viewer")

    try:
        user_id = create_user(username, password, clinic, role=role)
        click.echo(f"User '{username}' created successfully (id={user_id}, role={role}).")
    except ValueError as e:
        click.echo(f"Error: {e}")


# =====================================================================
# Run
# =====================================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
