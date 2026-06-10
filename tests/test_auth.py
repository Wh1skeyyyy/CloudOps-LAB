def test_register_success(client):
    res = client.post("/api/auth/register", json={
        "name": "Genesis", "email": "g@example.com", "password": "secret123",
    })
    assert res.status_code == 201
    data = res.get_json()
    assert "access_token" in data
    assert data["user"]["email"] == "g@example.com"
    assert "password" not in data["user"]
    assert "password_hash" not in data["user"]


def test_register_duplicate_email_returns_409(client):
    payload = {"name": "A", "email": "a@example.com", "password": "secret123"}
    client.post("/api/auth/register", json=payload)
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 409
    assert res.get_json()["error"] == "Conflict"


def test_register_short_password_returns_400(client):
    res = client.post("/api/auth/register", json={
        "name": "A", "email": "a@example.com", "password": "short",
    })
    assert res.status_code == 400


def test_register_missing_fields_returns_400(client):
    res = client.post("/api/auth/register", json={"email": "a@example.com"})
    assert res.status_code == 400
    assert "Missing required fields" in res.get_json()["message"]


def test_login_success_returns_token(client):
    client.post("/api/auth/register", json={
        "name": "A", "email": "a@example.com", "password": "secret123",
    })
    res = client.post("/api/auth/login", json={
        "email": "a@example.com", "password": "secret123",
    })
    assert res.status_code == 200
    assert "access_token" in res.get_json()


def test_login_wrong_password_returns_401(client):
    client.post("/api/auth/register", json={
        "name": "A", "email": "a@example.com", "password": "secret123",
    })
    res = client.post("/api/auth/login", json={
        "email": "a@example.com", "password": "wrong",
    })
    assert res.status_code == 401


def test_login_unknown_email_returns_401_same_message(client):
    """We must not reveal whether an email exists."""
    res = client.post("/api/auth/login", json={
        "email": "nobody@example.com", "password": "whatever",
    })
    assert res.status_code == 401
    assert res.get_json()["message"] == "Invalid email or password"


def test_profile_without_token_returns_401(client):
    res = client.get("/api/auth/profile")
    assert res.status_code == 401
    body = res.get_json()
    assert body["error"] == "Unauthorized"
    assert "message" in body


def test_profile_with_token_returns_user(client, auth_headers):
    res = client.get("/api/auth/profile", headers=auth_headers)
    assert res.status_code == 200
    assert res.get_json()["user"]["email"] == "test@example.com"
