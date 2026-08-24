"""
BactoAI Flask Application Factory
==================================
Creates and configures the Flask application with all extensions,
blueprints, and middleware registered.
"""

import os
import secrets
import traceback

from flask import Flask, request, jsonify
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from bactoai.config import Config
from bactoai.database import get_user_by_username, create_user
from bactoai.models.prediction import load_prediction_assets
from bactoai.routes.auth import auth_bp
from bactoai.routes.main import main_bp
from bactoai.routes.api import api_bp
from bactoai.routes.admin import admin_bp


csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])


@limiter.request_filter
def _exempt_static_from_rate_limit():
    """Static asset requests (CSS/JS/fonts) shouldn't count against the abuse-prevention quota."""
    return request.endpoint == "static"


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

    # Ensure default admin exists (Supabase persists data across deploys)
    with app.app_context():
        _create_default_admin()

    # Load prediction assets (skip in testing)
    if not app.config.get("SKIP_MODEL_LOADING"):
        load_prediction_assets(app)

    # ------------------------------------------------------------------
    # Global error handlers — return JSON for fetch/AJAX/API requests so
    # the frontend always gets a readable error instead of an HTML 500 page.
    # ------------------------------------------------------------------
    def _wants_json(req):
        if req.accept_mimetypes.best == "application/json":
            return True
        if req.headers.get("X-Requested-With", "").lower() == "xmlhttprequest":
            return True
        if req.is_json:
            return True
        return False

    @app.errorhandler(500)
    def _handle_500(error):
        app.logger.error(f"Unhandled server error: {error}\n{traceback.format_exc()}")
        if _wants_json(request):
            return jsonify({
                "error": "An unexpected server error occurred. Please try again. "
                         "If the problem persists, contact support."
            }), 500
        return error

    @app.errorhandler(503)
    def _handle_503(error):
        if _wants_json(request):
            return jsonify({
                "error": "Service temporarily unavailable. Please try again shortly."
            }), 503
        return error

    return app
