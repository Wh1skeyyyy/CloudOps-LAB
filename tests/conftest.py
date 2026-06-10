"""Shared pytest fixtures.

The `app` fixture creates a fresh Flask application bound to an in-memory
SQLite database for each test, so tests are isolated and don't leave state
behind. The `client` fixture is a Flask test client (no real HTTP). The
`auth_headers` fixture registers a user and returns ready-to-use Bearer
headers, since most endpoints require authentication.
"""
import pytest

from app import create_app
from app.extensions import db


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    """Register a user and return Authorization headers for them."""
    res = client.post("/api/auth/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "secret123",
    })
    assert res.status_code == 201, res.get_json()
    token = res.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def register_and_auth(client, email: str):
    """Helper used by tests that need a second user."""
    res = client.post("/api/auth/register", json={
        "name": email.split("@")[0],
        "email": email,
        "password": "secret123",
    })
    assert res.status_code == 201
    token = res.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
