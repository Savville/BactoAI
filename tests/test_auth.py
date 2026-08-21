"""
BactoAI Authentication Tests
==============================
Tests for user registration, login, logout, and role-based access.
"""

import pytest


class TestRegistration:
    """Tests for user registration."""

    def test_register_page_loads(self, client):
        """Registration page should load successfully."""
        response = client.get("/register")
        assert response.status_code == 200
        assert b"Create a new account" in response.data

    def test_register_success(self, client):
        """Successful registration should redirect to login."""
        response = client.post("/register", data={
            "username": "newuser",
            "password": "password123",
            "clinic_name": "Test Clinic",
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b"Registration successful" in response.data

    def test_register_duplicate_username(self, client):
        """Duplicate username should show error."""
        client.post("/register", data={
            "username": "duplicate",
            "password": "password123",
        })
        response = client.post("/register", data={
            "username": "duplicate",
            "password": "password123",
        }, follow_redirects=True)
        assert b"already exists" in response.data

    def test_register_short_password(self, client):
        """Password shorter than 6 chars should fail."""
        response = client.post("/register", data={
            "username": "shortpass",
            "password": "123",
        }, follow_redirects=True)
        assert b"at least 6 characters" in response.data

    def test_register_missing_fields(self, client):
        """Missing username or password should fail."""
        response = client.post("/register", data={
            "username": "",
            "password": "",
        }, follow_redirects=True)
        assert b"required" in response.data


class TestLogin:
    """Tests for user login."""

    def test_login_page_loads(self, client):
        """Login page should load successfully."""
        response = client.get("/login")
        assert response.status_code == 200
        assert b"Sign In" in response.data

    def test_login_success(self, client):
        """Successful login should redirect to index."""
        # Register first
        client.post("/register", data={
            "username": "logintest",
            "password": "password123",
        })
        response = client.post("/login", data={
            "username": "logintest",
            "password": "password123",
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_login_wrong_password(self, client):
        """Wrong password should show error."""
        client.post("/register", data={
            "username": "wrongpass",
            "password": "password123",
        })
        response = client.post("/login", data={
            "username": "wrongpass",
            "password": "wrongpassword",
        }, follow_redirects=True)
        assert b"Invalid" in response.data

    def test_login_nonexistent_user(self, client):
        """Nonexistent user should show error."""
        response = client.post("/login", data={
            "username": "nonexistent",
            "password": "password123",
        }, follow_redirects=True)
        assert b"Invalid" in response.data


class TestLogout:
    """Tests for user logout."""

    def test_logout(self, auth_client):
        """Logout should redirect to login."""
        response = auth_client.get("/logout", follow_redirects=True)
        assert response.status_code == 200
        assert b"Sign In" in response.data


class TestProtectedRoutes:
    """Tests for login-required routes."""

    def test_index_requires_login(self, client):
        """Index page should redirect to login when not authenticated."""
        response = client.get("/", follow_redirects=True)
        assert b"Sign In" in response.data

    def test_history_requires_login(self, client):
        """History page should redirect to login when not authenticated."""
        response = client.get("/history", follow_redirects=True)
        assert b"Sign In" in response.data

    def test_predict_requires_login(self, client):
        """Predict endpoint should redirect when not authenticated."""
        response = client.post("/predict", follow_redirects=True)
        assert b"Sign In" in response.data
