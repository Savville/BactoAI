"""
BactoAI Database Module
========================
Handles all database operations: connection management, initialization,
and data access for users, submissions, feedback, and audit logs.
"""

import os
import sqlite3
import secrets
import hashlib
from datetime import datetime

from flask import g, current_app


def get_db():
    """Get a database connection for the current request."""
    if "db" not in g:
        db_path = current_app.config.get("DB_PATH", "data/bactoai.db")
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")
        g.db.execute("PRAGMA foreign_keys=ON")
    return g.db


def close_db(exception=None):
    """Close the database connection at the end of a request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


DB_PATH = "data/bactoai.db"


def init_db():
    """Initialize the database schema."""
    db_path = DB_PATH
    # Ensure data directory exists (critical for Render deployments)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    db = sqlite3.connect(db_path)
    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            clinic_name TEXT,
            role TEXT DEFAULT 'viewer' CHECK(role IN ('admin', 'lab_tech', 'viewer')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            key_hash TEXT UNIQUE NOT NULL,
            key_prefix TEXT NOT NULL,
            name TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_used_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            sample_id TEXT NOT NULL,
            filename TEXT,
            genome_size INTEGER,
            meropenem_label TEXT,
            meropenem_prob REAL,
            meropenem_confidence TEXT,
            ciprofloxacin_label TEXT,
            ciprofloxacin_prob REAL,
            ciprofloxacin_confidence TEXT,
            cefotaxime_label TEXT,
            cefotaxime_prob REAL,
            cefotaxime_confidence TEXT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            submission_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            antibiotic TEXT NOT NULL,
            predicted_label TEXT NOT NULL,
            actual_label TEXT NOT NULL,
            actual_value TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (submission_id) REFERENCES submissions(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            details TEXT,
            ip_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE INDEX IF NOT EXISTS idx_submissions_user ON submissions(user_id);
        CREATE INDEX IF NOT EXISTS idx_submissions_date ON submissions(submitted_at);
        CREATE INDEX IF NOT EXISTS idx_submissions_sample ON submissions(sample_id);
        CREATE INDEX IF NOT EXISTS idx_feedback_submission ON feedback(submission_id);
        CREATE INDEX IF NOT EXISTS idx_feedback_user ON feedback(user_id);
        CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_log(user_id);
        CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON api_keys(key_hash);
    """)
    db.commit()
    db.close()


# =====================================================================
# Password Hashing
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
    """Get a user by username."""
    db = get_db()
    return db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()


def get_user_by_id(user_id):
    """Get a user by ID."""
    db = get_db()
    return db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def create_user(username, password, clinic_name="", role="viewer"):
    """Create a new user. Returns the user ID or raises ValueError."""
    db = get_db()
    existing = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
    if existing:
        raise ValueError("Username already exists")

    cursor = db.execute(
        "INSERT INTO users (username, password_hash, clinic_name, role) VALUES (?, ?, ?, ?)",
        (username, hash_password(password), clinic_name, role),
    )
    db.commit()
    return cursor.lastrowid


# =====================================================================
# API Key Operations
# =====================================================================

def create_api_key(user_id, name=""):
    """Create a new API key. Returns the raw key (store securely!)."""
    raw_key = secrets.token_hex(32)
    key_prefix = raw_key[:8]
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

    db = get_db()
    db.execute(
        "INSERT INTO api_keys (user_id, key_hash, key_prefix, name) VALUES (?, ?, ?, ?)",
        (user_id, key_hash, key_prefix, name),
    )
    db.commit()
    return raw_key


def verify_api_key(raw_key):
    """Verify an API key and return the associated user_id."""
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    db = get_db()
    row = db.execute(
        "SELECT * FROM api_keys WHERE key_hash = ? AND is_active = 1", (key_hash,)
    ).fetchone()
    if row:
        db.execute(
            "UPDATE api_keys SET last_used_at = ? WHERE id = ?",
            (datetime.now().isoformat(), row["id"]),
        )
        db.commit()
        return row["user_id"]
    return None


def get_user_api_keys(user_id):
    """Get all API keys for a user (without hashes)."""
    db = get_db()
    return db.execute(
        "SELECT id, key_prefix, name, is_active, created_at, last_used_at "
        "FROM api_keys WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,),
    ).fetchall()


# =====================================================================
# Submission Operations
# =====================================================================

def save_submission(user_id, sample_id, filename, genome_size, results, notes=None):
    """Save a prediction submission."""
    db = get_db()
    result_map = {r["antibiotic"].lower(): r for r in results}
    db.execute(
        """INSERT INTO submissions
           (user_id, sample_id, filename, genome_size,
            meropenem_label, meropenem_prob, meropenem_confidence,
            ciprofloxacin_label, ciprofloxacin_prob, ciprofloxacin_confidence,
            cefotaxime_label, cefotaxime_prob, cefotaxime_confidence,
            notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            user_id, sample_id, filename, genome_size,
            result_map.get("meropenem", {}).get("label"),
            result_map.get("meropenem", {}).get("probability"),
            result_map.get("meropenem", {}).get("confidence"),
            result_map.get("ciprofloxacin", {}).get("label"),
            result_map.get("ciprofloxacin", {}).get("probability"),
            result_map.get("ciprofloxacin", {}).get("confidence"),
            result_map.get("cefotaxime", {}).get("label"),
            result_map.get("cefotaxime", {}).get("probability"),
            result_map.get("cefotaxime", {}).get("confidence"),
            notes,
        ),
    )
    db.commit()
    return db.execute("SELECT last_insert_rowid()").fetchone()[0]


def get_user_submissions(user_id, limit=100):
    """Get submission history for a user."""
    db = get_db()
    return db.execute(
        """SELECT * FROM submissions WHERE user_id = ?
           ORDER BY submitted_at DESC LIMIT ?""",
        (user_id, limit),
    ).fetchall()


def get_submission_by_id(submission_id):
    """Get a single submission by ID."""
    db = get_db()
    return db.execute("SELECT * FROM submissions WHERE id = ?", (submission_id,)).fetchone()


def get_all_submissions(limit=1000):
    """Get all submissions (for admin)."""
    db = get_db()
    return db.execute(
        """SELECT s.*, u.username, u.clinic_name
           FROM submissions s
           JOIN users u ON s.user_id = u.id
           ORDER BY s.submitted_at DESC LIMIT ?""",
        (limit,),
    ).fetchall()


# =====================================================================
# Feedback Operations
# =====================================================================

def save_feedback(submission_id, user_id, antibiotic, predicted_label, actual_label, actual_value=None, notes=None):
    """Save lab-confirmed feedback for a prediction."""
    db = get_db()
    db.execute(
        """INSERT INTO feedback
           (submission_id, user_id, antibiotic, predicted_label, actual_label, actual_value, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (submission_id, user_id, antibiotic, predicted_label, actual_label, actual_value, notes),
    )
    db.commit()


def get_submission_feedback(submission_id):
    """Get all feedback for a submission."""
    db = get_db()
    return db.execute(
        "SELECT * FROM feedback WHERE submission_id = ? ORDER BY created_at DESC",
        (submission_id,),
    ).fetchall()


def get_feedback_stats():
    """Get aggregate feedback statistics per antibiotic."""
    db = get_db()
    return db.execute(
        """SELECT antibiotic,
                  COUNT(*) as total,
                  SUM(CASE WHEN predicted_label = actual_label THEN 1 ELSE 0 END) as correct
           FROM feedback
           GROUP BY antibiotic"""
    ).fetchall()


# =====================================================================
# Audit Log
# =====================================================================

def log_action(user_id, action, details=None, ip_address=None):
    """Log an action to the audit log."""
    db = get_db()
    db.execute(
        "INSERT INTO audit_log (user_id, action, details, ip_address) VALUES (?, ?, ?, ?)",
        (user_id, action, details, ip_address),
    )
    db.commit()


# =====================================================================
# Admin Stats
# =====================================================================

def get_admin_stats():
    """Get system-wide statistics for the admin dashboard."""
    db = get_db()
    stats = {}
    stats["total_users"] = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    stats["total_submissions"] = db.execute("SELECT COUNT(*) FROM submissions").fetchone()[0]
    stats["total_feedback"] = db.execute("SELECT COUNT(*) FROM feedback").fetchone()[0]
    stats["recent_submissions"] = db.execute(
        "SELECT COUNT(*) FROM submissions WHERE submitted_at >= datetime('now', '-7 days')"
    ).fetchone()[0]
    stats["users_by_role"] = db.execute(
        "SELECT role, COUNT(*) as count FROM users GROUP BY role"
    ).fetchall()
    stats["submissions_per_day"] = db.execute(
        "SELECT DATE(submitted_at) as day, COUNT(*) as count "
        "FROM submissions GROUP BY day ORDER BY day DESC LIMIT 30"
    ).fetchall()
    return stats
