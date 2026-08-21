"""
BactoAI Test Configuration
============================
Shared fixtures for the test suite.
"""

import os
import sys
import tempfile
import pytest

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from bactoai.app import create_app
from bactoai.config import TestingConfig
from bactoai.database import get_db, close_db, init_db


@pytest.fixture
def app():
    """Create a test application instance."""
    # Create a temp directory for test data
    with tempfile.TemporaryDirectory() as tmpdir:
        # Override config to use temp directory
        class TestConfig(TestingConfig):
            def __init__(self):
                pass

        test_config = TestingConfig()
        test_config.DB_PATH = os.path.join(tmpdir, "test.db")

        app = create_app(config_class=TestingConfig)

        # Override the DB_PATH after creation
        app.config["DB_PATH"] = os.path.join(tmpdir, "test.db")

        with app.app_context():
            init_db()
            yield app


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def auth_client(client):
    """Create an authenticated test client with a test user."""
    # Register a test user
    client.post("/register", data={
        "username": "testuser",
        "password": "testpass123",
        "clinic_name": "Test Hospital",
    })
    # Login
    client.post("/login", data={
        "username": "testuser",
        "password": "testpass123",
    })
    return client


@pytest.fixture
def admin_client(client):
    """Create an authenticated admin test client."""
    # Register
    client.post("/register", data={
        "username": "adminuser",
        "password": "adminpass123",
        "clinic_name": "Admin Hospital",
    })
    # Set as admin directly in DB
    from bactoai.database import get_db
    with client.session_transaction() as sess:
        pass  # Force session creation

    # We need to modify the user role after creation
    # First get the app context
    from flask import current_app
    with current_app.app_context():
        db = get_db()
        db.execute("UPDATE users SET role = 'admin' WHERE username = 'adminuser'")
        db.commit()

    # Login
    client.post("/login", data={
        "username": "adminuser",
        "password": "adminpass123",
    })
    return client


def create_test_fasta(path, content=">test_genome\nACGTACGTACGTACGTACGTACGTACGTACGTACGT\n"):
    """Helper to create a test FASTA file."""
    with open(path, "w") as f:
        f.write(content)
