"""
BactoAI Flask Application Factory
==================================
Creates and configures the Flask application with all extensions,
blueprints, and middleware registered.
"""

import os
import secrets

from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from bactoai.config import Config
from bactoai.database import init_db, DB_PATH, get_user_by_username, create_user
from bactoai.models.prediction import load_prediction_assets
from bactoai.routes.auth import auth_bp
from bactoai.routes.main import main_bp
from bactoai.routes.api import api_bp
from bactoai.routes.admin import admin_bp


csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])


def _create_default_admin():
    """Create default admin user from environment variables (runs every startup)."""
    try:
        admin_user = os.environ.get("BACTOAI_ADMIN_USER", "bactoai")
        admin_pass = os.environ.get("BACTOAI_ADMIN_PASS", "admin123")
        admin_clinic = os.environ.get("BACTOAI_ADMIN_CLINIC", "BactoAI Admin")

        # Always ensure admin exists (Render has ephemeral filesystem)
        existing = get_user_by_username(admin_user)
        if existing is None:
            create_user(
                username=admin_user,
                password=admin_pass,
                clinic_name=admin_clinic,
                role="admin"
            )
    except Exception as e:
        import logging
        logging.warning(f"Failed to create default admin: {e}")


def create_app(config_class=Config):
    """Application factory for BactoAI."""
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates"),
        static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), "static"),
    )
    app.config.from_object(config_class)

    # Initialize extensions
    csrf.init_app(app)
    limiter.init_app(app)

    # Exempt API routes from CSRF (they use API key auth)
    csrf.exempt(api_bp)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix="/api/v1")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # Ensure database exists and create default admin
    with app.app_context():
        init_db()
        _create_default_admin()

    # Load prediction assets (skip in testing)
    if not app.config.get("SKIP_MODEL_LOADING"):
        load_prediction_assets(app)

    return app
