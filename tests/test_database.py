"""
BactoAI Database Tests
========================
Tests for database operations: users, submissions, feedback, audit log.
"""

import pytest
from bactoai.database import (
    hash_password, verify_password,
    create_user, get_user_by_username, get_user_by_id,
    save_submission, get_user_submissions, get_submission_by_id,
    save_feedback, get_submission_feedback, get_feedback_stats,
    log_action, create_api_key, verify_api_key, get_admin_stats,
)


class TestPasswordHashing:
    """Tests for password hashing and verification."""

    def test_hash_password_returns_string(self):
        """Password hash should be a non-empty string."""
        result = hash_password("testpassword")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_verify_correct_password(self):
        """Correct password should verify successfully."""
        hashed = hash_password("mypassword")
        assert verify_password(hashed, "mypassword") is True

    def test_verify_wrong_password(self):
        """Wrong password should fail verification."""
        hashed = hash_password("mypassword")
        assert verify_password(hashed, "wrongpassword") is False

    def test_different_salts(self):
        """Same password should produce different hashes (different salts)."""
        hash1 = hash_password("samepassword")
        hash2 = hash_password("samepassword")
        assert hash1 != hash2


class TestUserOperations:
    """Tests for user CRUD operations."""

    def test_create_user(self, app):
        """Creating a user should return a user ID."""
        with app.app_context():
            user_id = create_user("testuser", "password123", "Test Clinic")
            assert isinstance(user_id, int)
            assert user_id > 0

    def test_create_duplicate_user(self, app):
        """Creating a duplicate user should raise ValueError."""
        with app.app_context():
            create_user("uniqueuser", "password123")
            with pytest.raises(ValueError):
                create_user("uniqueuser", "password456")

    def test_get_user_by_username(self, app):
        """Should retrieve a user by username."""
        with app.app_context():
            create_user("findme", "password123", "My Clinic")
            user = get_user_by_username("findme")
            assert user is not None
            assert user["username"] == "findme"
            assert user["clinic_name"] == "My Clinic"

    def test_get_user_by_id(self, app):
        """Should retrieve a user by ID."""
        with app.app_context():
            user_id = create_user("byid", "password123")
            user = get_user_by_id(user_id)
            assert user is not None
            assert user["username"] == "byid"

    def test_default_role_is_viewer(self, app):
        """New users should have 'viewer' role by default."""
        with app.app_context():
            create_user("rolecheck", "password123")
            user = get_user_by_username("rolecheck")
            assert user["role"] == "viewer"


class TestSubmissionOperations:
    """Tests for submission CRUD operations."""

    def test_save_submission(self, app):
        """Saving a submission should return the submission ID."""
        with app.app_context():
            user_id = create_user("submitter", "password123")
            results = [
                {"antibiotic": "Meropenem", "label": "RESISTANT", "probability": 0.85, "confidence": "HIGH"},
                {"antibiotic": "Ciprofloxacin", "label": "SUSCEPTIBLE", "probability": 0.2, "confidence": "HIGH"},
                {"antibiotic": "Cefotaxime", "label": "RESISTANT", "probability": 0.7, "confidence": "MEDIUM"},
            ]
            sub_id = save_submission(user_id, "SAMPLE-001", "test.fna", 5000000, results)
            assert isinstance(sub_id, int)
            assert sub_id > 0

    def test_get_user_submissions(self, app):
        """Should retrieve submissions for a user."""
        with app.app_context():
            user_id = create_user("historyuser", "password123")
            results = [
                {"antibiotic": "Meropenem", "label": "RESISTANT", "probability": 0.85, "confidence": "HIGH"},
                {"antibiotic": "Ciprofloxacin", "label": "SUSCEPTIBLE", "probability": 0.2, "confidence": "HIGH"},
                {"antibiotic": "Cefotaxime", "label": "RESISTANT", "probability": 0.7, "confidence": "MEDIUM"},
            ]
            save_submission(user_id, "SAMPLE-001", "test.fna", 5000000, results)
            submissions = get_user_submissions(user_id)
            assert len(submissions) == 1
            assert submissions[0]["sample_id"] == "SAMPLE-001"

    def test_get_submission_by_id(self, app):
        """Should retrieve a specific submission."""
        with app.app_context():
            user_id = create_user("specificsub", "password123")
            results = [
                {"antibiotic": "Meropenem", "label": "RESISTANT", "probability": 0.85, "confidence": "HIGH"},
                {"antibiotic": "Ciprofloxacin", "label": "SUSCEPTIBLE", "probability": 0.2, "confidence": "HIGH"},
                {"antibiotic": "Cefotaxime", "label": "RESISTANT", "probability": 0.7, "confidence": "MEDIUM"},
            ]
            sub_id = save_submission(user_id, "SPEC-001", "test.fna", 5000000, results)
            sub = get_submission_by_id(sub_id)
            assert sub is not None
            assert sub["sample_id"] == "SPEC-001"


class TestFeedbackOperations:
    """Tests for feedback operations."""

    def test_save_feedback(self, app):
        """Saving feedback should succeed."""
        with app.app_context():
            user_id = create_user("feedbackuser", "password123")
            results = [
                {"antibiotic": "Meropenem", "label": "RESISTANT", "probability": 0.85, "confidence": "HIGH"},
                {"antibiotic": "Ciprofloxacin", "label": "SUSCEPTIBLE", "probability": 0.2, "confidence": "HIGH"},
                {"antibiotic": "Cefotaxime", "label": "RESISTANT", "probability": 0.7, "confidence": "MEDIUM"},
            ]
            sub_id = save_submission(user_id, "FB-001", "test.fna", 5000000, results)
            save_feedback(sub_id, user_id, "meropenem", "RESISTANT", "RESISTANT", ">32", "Confirmed by lab")

            feedback = get_submission_feedback(sub_id)
            assert len(feedback) == 1
            assert feedback[0]["antibiotic"] == "meropenem"
            assert feedback[0]["actual_label"] == "RESISTANT"

    def test_get_feedback_stats(self, app):
        """Should calculate feedback statistics."""
        with app.app_context():
            user_id = create_user("statsuser", "password123")
            results = [
                {"antibiotic": "Meropenem", "label": "RESISTANT", "probability": 0.85, "confidence": "HIGH"},
                {"antibiotic": "Ciprofloxacin", "label": "SUSCEPTIBLE", "probability": 0.2, "confidence": "HIGH"},
                {"antibiotic": "Cefotaxime", "label": "RESISTANT", "probability": 0.7, "confidence": "MEDIUM"},
            ]
            sub_id = save_submission(user_id, "STAT-001", "test.fna", 5000000, results)
            save_feedback(sub_id, user_id, "meropenem", "RESISTANT", "RESISTANT")
            save_feedback(sub_id, user_id, "ciprofloxacin", "SUSCEPTIBLE", "RESISTANT")

            stats = get_feedback_stats()
            assert len(stats) >= 2


class TestApiKeyOperations:
    """Tests for API key operations."""

    def test_create_api_key(self, app):
        """Creating an API key should return a raw key."""
        with app.app_context():
            user_id = create_user("apiuser", "password123")
            raw_key = create_api_key(user_id, "Test Key")
            assert isinstance(raw_key, str)
            assert len(raw_key) == 64  # 32 bytes hex = 64 chars

    def test_verify_api_key(self, app):
        """Verifying a valid API key should return the user_id."""
        with app.app_context():
            user_id = create_user("apiuser2", "password123")
            raw_key = create_api_key(user_id, "Test Key")
            verified_id = verify_api_key(raw_key)
            assert verified_id == user_id

    def test_verify_invalid_api_key(self, app):
        """Verifying an invalid API key should return None."""
        with app.app_context():
            result = verify_api_key("invalid_key_here")
            assert result is None


class TestAuditLog:
    """Tests for audit logging."""

    def test_log_action(self, app):
        """Logging an action should succeed."""
        with app.app_context():
            user_id = create_user("audituser", "password123")
            log_action(user_id, "test_action", "Test details", "127.0.0.1")

            from bactoai.database import get_db
            db = get_db()
            logs = db.execute(
                "SELECT * FROM audit_log WHERE user_id = ?", (user_id,)
            ).fetchall()
            assert len(logs) == 1
            assert logs[0]["action"] == "test_action"


class TestAdminStats:
    """Tests for admin statistics."""

    def test_get_admin_stats(self, app):
        """Should return system-wide statistics."""
        with app.app_context():
            create_user("statsuser1", "password123")
            create_user("statsuser2", "password123")
            stats = get_admin_stats()
            assert "total_users" in stats
            assert stats["total_users"] >= 2
            assert "total_submissions" in stats
            assert "total_feedback" in stats
