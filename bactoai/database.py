"""
BactoAI Database Module (Supabase)
====================================
Handles all database operations using Supabase (PostgreSQL).
All data persists across Render deploys — no more SQLite wiping.

Tables required in Supabase (run the SQL in migrations/supabase_setup.sql):
- users
- api_keys
- submissions
- feedback
- audit_log
"""

import os
import secrets
import hashlib
from datetime import datetime, timedelta

from supabase import create_client, Client


# =====================================================================
# Supabase Client
# =====================================================================

_supabase_client: Client = None


def get_supabase() -> Client:
    """Get or create the Supabase client singleton."""
    global _supabase_client
    if _supabase_client is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        if not url or not key:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_KEY environment variables must be set. "
                "Add them to your .env file or Render environment variables."
            )
        _supabase_client = create_client(url, key)
    return _supabase_client


# =====================================================================
# Password Hashing (unchanged — still local)
# =====================================================================

def hash_password(password):
    """Hash a password with PBKDF2-HMAC-SHA256."""
    salt = secrets.token_hex(16)
    pw_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
    return salt + pw_hash.hex()


def verify_password(stored, password):
    """Verify a password against its hash."""
    salt = stored[:32]
    pw_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
    return stored[32:] == pw_hash.hex()


# =====================================================================
# User Operations
# =====================================================================

def get_user_by_username(username):
    """Get a user by username. Returns dict or None."""
    sb = get_supabase()
    result = sb.table("users").select("*").eq("username", username).execute()
    if result.data and len(result.data) > 0:
        return result.data[0]
    return None


def get_user_by_id(user_id):
    """Get a user by ID. Returns dict or None."""
    sb = get_supabase()
    result = sb.table("users").select("*").eq("id", user_id).execute()
    if result.data and len(result.data) > 0:
        return result.data[0]
    return None


def create_user(username, password, clinic_name="", role="viewer"):
    """Create a new user. Returns the user ID or raises ValueError."""
    sb = get_supabase()
    existing = get_user_by_username(username)
    if existing:
        raise ValueError("Username already exists")

    result = sb.table("users").insert({
        "username": username,
        "password_hash": hash_password(password),
        "clinic_name": clinic_name,
        "role": role,
    }).execute()

    if result.data and len(result.data) > 0:
        return result.data[0]["id"]
    raise RuntimeError("Failed to create user")


# =====================================================================
# API Key Operations
# =====================================================================

def create_api_key(user_id, name=""):
    """Create a new API key. Returns the raw key (store securely!)."""
    raw_key = secrets.token_hex(32)
    key_prefix = raw_key[:8]
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

    sb = get_supabase()
    sb.table("api_keys").insert({
        "user_id": user_id,
        "key_hash": key_hash,
        "key_prefix": key_prefix,
        "name": name,
    }).execute()
    return raw_key


def verify_api_key(raw_key):
    """Verify an API key and return the associated user_id. Returns None if invalid."""
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    sb = get_supabase()
    result = sb.table("api_keys").select("*").eq("key_hash", key_hash).eq("is_active", True).execute()

    if result.data and len(result.data) > 0:
        row = result.data[0]
        # Update last_used_at
        sb.table("api_keys").update({
            "last_used_at": datetime.now().isoformat()
        }).eq("id", row["id"]).execute()
        return row["user_id"]
    return None


def get_user_api_keys(user_id):
    """Get all API keys for a user (without hashes)."""
    sb = get_supabase()
    result = (
        sb.table("api_keys")
        .select("id, key_prefix, name, is_active, created_at, last_used_at")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data or []


# =====================================================================
# Submission Operations
# =====================================================================

def save_submission(user_id, sample_id, filename, genome_size, results, notes=None):
    """Save a prediction submission. Returns the submission ID."""
    sb = get_supabase()
    result_map = {r["antibiotic"].lower(): r for r in results}

    data = {
        "user_id": user_id,
        "sample_id": sample_id,
        "filename": filename,
        "genome_size": genome_size,
        "meropenem_label": result_map.get("meropenem", {}).get("label"),
        "meropenem_prob": result_map.get("meropenem", {}).get("probability"),
        "meropenem_confidence": result_map.get("meropenem", {}).get("confidence"),
        "ciprofloxacin_label": result_map.get("ciprofloxacin", {}).get("label"),
        "ciprofloxacin_prob": result_map.get("ciprofloxacin", {}).get("probability"),
        "ciprofloxacin_confidence": result_map.get("ciprofloxacin", {}).get("confidence"),
        "cefotaxime_label": result_map.get("cefotaxime", {}).get("label"),
        "cefotaxime_prob": result_map.get("cefotaxime", {}).get("probability"),
        "cefotaxime_confidence": result_map.get("cefotaxime", {}).get("confidence"),
        "notes": notes,
    }

    result = sb.table("submissions").insert(data).execute()
    if result.data and len(result.data) > 0:
        return result.data[0]["id"]
    raise RuntimeError("Failed to save submission")


def get_user_submissions(user_id, limit=100):
    """Get submission history for a user."""
    sb = get_supabase()
    result = (
        sb.table("submissions")
        .select("*")
        .eq("user_id", user_id)
        .order("submitted_at", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data or []


def get_submission_by_id(submission_id):
    """Get a single submission by ID."""
    sb = get_supabase()
    result = sb.table("submissions").select("*").eq("id", submission_id).execute()
    if result.data and len(result.data) > 0:
        return result.data[0]
    return None


def get_all_submissions(limit=1000):
    """Get all submissions with user info (for admin)."""
    sb = get_supabase()
    # Supabase Python client doesn't support JOIN directly via builder,
    # so we fetch submissions and users separately and merge in Python
    subs_result = (
        sb.table("submissions")
        .select("*")
        .order("submitted_at", desc=True)
        .limit(limit)
        .execute()
    )
    subs = subs_result.data or []
    if not subs:
        return []

    user_ids = list(set(s["user_id"] for s in subs))
    users_result = sb.table("users").select("id, username, clinic_name").in_("id", user_ids).execute()
    users_map = {u["id"]: u for u in (users_result.data or [])}

    # Merge user info into submissions
    for sub in subs:
        user = users_map.get(sub["user_id"], {})
        sub["username"] = user.get("username")
        sub["clinic_name"] = user.get("clinic_name")

    return subs


# =====================================================================
# Feedback Operations
# =====================================================================

def save_feedback(submission_id, user_id, antibiotic, predicted_label, actual_label, actual_value=None, notes=None):
    """Save lab-confirmed feedback for a prediction."""
    sb = get_supabase()
    sb.table("feedback").insert({
        "submission_id": submission_id,
        "user_id": user_id,
        "antibiotic": antibiotic,
        "predicted_label": predicted_label,
        "actual_label": actual_label,
        "actual_value": actual_value,
        "notes": notes,
    }).execute()


def get_submission_feedback(submission_id):
    """Get all feedback for a submission."""
    sb = get_supabase()
    result = (
        sb.table("feedback")
        .select("*")
        .eq("submission_id", submission_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data or []


def get_feedback_stats():
    """Get aggregate feedback statistics per antibiotic."""
    sb = get_supabase()
    result = sb.table("feedback").select("antibiotic, predicted_label, actual_label").execute()
    rows = result.data or []

    # Aggregate in Python
    stats = {}
    for row in rows:
        ab = row["antibiotic"]
        if ab not in stats:
            stats[ab] = {"antibiotic": ab, "total": 0, "correct": 0}
        stats[ab]["total"] += 1
        if row["predicted_label"] == row["actual_label"]:
            stats[ab]["correct"] += 1

    return list(stats.values())


# =====================================================================
# Audit Log
# =====================================================================

def log_action(user_id, action, details=None, ip_address=None):
    """Log an action to the audit log."""
    sb = get_supabase()
    sb.table("audit_log").insert({
        "user_id": user_id,
        "action": action,
        "details": details,
        "ip_address": ip_address,
    }).execute()


# =====================================================================
# Admin Stats
# =====================================================================

def get_admin_stats():
    """Get system-wide statistics for the admin dashboard."""
    sb = get_supabase()
    stats = {}

    # Total users
    result = sb.table("users").select("id", count="exact").execute()
    stats["total_users"] = result.count or 0

    # Total submissions
    result = sb.table("submissions").select("id", count="exact").execute()
    stats["total_submissions"] = result.count or 0

    # Total feedback
    result = sb.table("feedback").select("id", count="exact").execute()
    stats["total_feedback"] = result.count or 0

    # Recent submissions (last 7 days)
    seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
    result = (
        sb.table("submissions")
        .select("id", count="exact")
        .gte("submitted_at", seven_days_ago)
        .execute()
    )
    stats["recent_submissions"] = result.count or 0

    # Users by role
    result = sb.table("users").select("role").execute()
    role_counts = {}
    for row in (result.data or []):
        role = row["role"]
        role_counts[role] = role_counts.get(role, 0) + 1
    stats["users_by_role"] = [
        {"role": k, "count": v} for k, v in role_counts.items()
    ]

    # Submissions per day (last 30 days)
    thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
    result = (
        sb.table("submissions")
        .select("submitted_at")
        .gte("submitted_at", thirty_days_ago)
        .execute()
    )
    day_counts = {}
    for row in (result.data or []):
        day = row["submitted_at"][:10]  # Extract YYYY-MM-DD
        day_counts[day] = day_counts.get(day, 0) + 1
    stats["submissions_per_day"] = sorted(
        [{"day": k, "count": v} for k, v in day_counts.items()],
        key=lambda x: x["day"],
        reverse=True
    )

    return stats
