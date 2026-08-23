"""
BactoAI Test Configuration
============================
Shared fixtures for the test suite.
Uses Supabase for database operations.
"""

import os
import sys
import pytest

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from bactoai.app import create_app
from bactoai.config import TestingConfig
from bactoai.database import get_supabase


@pytest.fixture
def app():
    """Create a test application instance."""
    app = create_app(config_class=TestingConfig)
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

    # Set as admin directly via Supabase
    sb = get_supabase()
    sb.table("users").update({"role": "admin"}).eq("username", "adminuser").execute()

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
