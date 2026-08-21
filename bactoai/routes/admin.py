"""
BactoAI Admin Routes
=====================
Admin dashboard and management endpoints.
Only accessible to users with the 'admin' role.
"""

from flask import (
    Blueprint, render_template, session, redirect, url_for, flash, jsonify, request,
)

from bactoai.database import (
    get_db, get_admin_stats, get_all_submissions,
    get_feedback_stats, log_action,
)
from bactoai.routes.auth import login_required, role_required


admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/")
@login_required
@role_required("admin")
def dashboard():
    """Admin dashboard with system-wide statistics."""
    stats = get_admin_stats()
    feedback_stats = get_feedback_stats()
    recent_submissions = get_all_submissions(limit=50)

    return render_template(
        "admin/dashboard.html",
        stats=stats,
        feedback_stats=feedback_stats,
        recent_submissions=recent_submissions,
        username=session.get("username"),
    )


@admin_bp.route("/users")
@login_required
@role_required("admin")
def users():
    """Admin user management page."""
    db = get_db()
    all_users = db.execute(
        "SELECT id, username, clinic_name, role, created_at, is_active "
        "FROM users ORDER BY created_at DESC"
    ).fetchall()

    return render_template(
        "admin/users.html",
        users=all_users,
        username=session.get("username"),
    )


@admin_bp.route("/users/<int:user_id>/role", methods=["POST"])
@login_required
@role_required("admin")
def update_user_role(user_id):
    """Update a user's role."""
    new_role = request.form.get("role", "").strip()
    if new_role not in ("admin", "lab_tech", "viewer"):
        flash("Invalid role.", "error")
        return redirect(url_for("admin.users"))

    db = get_db()
    db.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
    db.commit()

    log_action(
        session["user_id"], "update_role",
        f"User {user_id} role changed to {new_role}",
    )
    flash(f"User role updated to {new_role}.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/toggle", methods=["POST"])
@login_required
@role_required("admin")
def toggle_user(user_id):
    """Activate/deactivate a user account."""
    db = get_db()
    db.execute(
        "UPDATE users SET is_active = NOT is_active WHERE id = ?", (user_id,)
    )
    db.commit()

    log_action(session["user_id"], "toggle_user", f"User {user_id} toggled")
    flash("User status updated.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/stats")
@login_required
@role_required("admin")
def stats_json():
    """Get admin statistics as JSON."""
    return jsonify(get_admin_stats())
