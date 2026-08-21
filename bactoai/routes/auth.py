"""
BactoAI Authentication Routes
==============================
Handles user registration, login, logout, and API key management.
"""

from functools import wraps

from flask import (
    Blueprint, render_template, request, session,
    redirect, url_for, flash, current_app,
)

from bactoai.database import (
    get_db, get_user_by_username, get_user_by_id,
    create_user, verify_password, log_action,
    create_api_key, get_user_api_keys,
)


auth_bp = Blueprint("auth", __name__)


# =====================================================================
# Role-based access control
# =====================================================================

def login_required(f):
    """Decorator to require login for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    """Decorator to require specific role(s) for a route."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("auth.login"))
            user = get_user_by_id(session["user_id"])
            if not user or user["role"] not in roles:
                flash("You do not have permission to access this page.", "error")
                return redirect(url_for("main.index"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# =====================================================================
# Auth Routes
# =====================================================================

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = get_user_by_username(username)

        if user and verify_password(user["password_hash"], password):
            if not user["is_active"]:
                flash("Account is deactivated. Contact an administrator.", "error")
                return render_template("login.html")

            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["clinic_name"] = user["clinic_name"]
            session["role"] = user["role"]
            log_action(user["id"], "login", ip_address=request.remote_addr)
            return redirect(url_for("main.index"))

        flash("Invalid username or password.", "error")
    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Handle user registration."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        clinic_name = request.form.get("clinic_name", "").strip()

        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return render_template("register.html")

        try:
            create_user(username, password, clinic_name, role="viewer")
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("auth.login"))
        except ValueError as e:
            flash(str(e), "error")

    return render_template("register.html")


@auth_bp.route("/logout")
def logout():
    """Handle user logout."""
    if "user_id" in session:
        log_action(session["user_id"], "logout", ip_address=request.remote_addr)
    session.clear()
    return redirect(url_for("auth.login"))


# =====================================================================
# API Key Management
# =====================================================================

@auth_bp.route("/api-keys", methods=["GET", "POST"])
@login_required
def api_keys():
    """Manage API keys for the authenticated user."""
    if request.method == "POST":
        name = request.form.get("name", "").strip() or "API Key"
        raw_key = create_api_key(session["user_id"], name)
        flash(f"API key created: {raw_key} — Save this now, it won't be shown again!", "success")

    keys = get_user_api_keys(session["user_id"])
    return render_template("api_keys.html", api_keys=keys, username=session.get("username"))
