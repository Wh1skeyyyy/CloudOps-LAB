from tests.conftest import register_and_auth


def _make_service(client, headers, **fields):
    return client.post("/api/services", json={"name": "Test API", **fields}, headers=headers)


# --- Create ---

def test_create_service_returns_201_with_owner(client, auth_headers):
    res = client.post("/api/services", json={
        "name": "Note2Quiz API",
        "service_type": "backend",
        "environment": "production",
    }, headers=auth_headers)
    assert res.status_code == 201
    service = res.get_json()["service"]
    assert service["name"] == "Note2Quiz API"
    assert service["user_id"] == 1


def test_create_service_without_token_returns_401(client):
    res = client.post("/api/services", json={"name": "X"})
    assert res.status_code == 401


def test_create_service_requires_name(client, auth_headers):
    res = client.post("/api/services", json={"environment": "production"}, headers=auth_headers)
    assert res.status_code == 400


def test_create_service_rejects_invalid_environment(client, auth_headers):
    res = client.post("/api/services", json={
        "name": "X", "environment": "spaceship",
    }, headers=auth_headers)
    assert res.status_code == 400
    assert "environment must be one of" in res.get_json()["message"]


def test_create_service_rejects_invalid_url(client, auth_headers):
    res = client.post("/api/services", json={
        "name": "X", "repository_url": "not-a-url",
    }, headers=auth_headers)
    assert res.status_code == 400


# --- List + filter ---

def test_list_services_returns_only_own(client):
    headers_a = register_and_auth(client, "a@example.com")
    headers_b = register_and_auth(client, "b@example.com")

    _make_service(client, headers_a, name="A's service")

    res = client.get("/api/services", headers=headers_b)
    assert res.status_code == 200
    body = res.get_json()
    assert body["count"] == 0
    assert body["services"] == []


def test_filter_by_environment(client, auth_headers):
    _make_service(client, auth_headers, name="prod", environment="production")
    _make_service(client, auth_headers, name="dev", environment="development")

    res = client.get("/api/services?environment=production", headers=auth_headers)
    services = res.get_json()["services"]
    assert len(services) == 1
    assert services[0]["name"] == "prod"


def test_filter_by_provider_and_health(client, auth_headers):
    _make_service(client, auth_headers, name="a", provider="AWS", health_status="healthy")
    _make_service(client, auth_headers, name="b", provider="Render", health_status="down")
    _make_service(client, auth_headers, name="c", provider="AWS", health_status="down")

    res = client.get("/api/services?provider=AWS&health_status=down", headers=auth_headers)
    services = res.get_json()["services"]
    assert len(services) == 1
    assert services[0]["name"] == "c"


# --- Ownership ---

def test_user_cannot_read_others_service(client):
    headers_a = register_and_auth(client, "a@example.com")
    headers_b = register_and_auth(client, "b@example.com")

    create = _make_service(client, headers_a, name="A's secret")
    service_id = create.get_json()["service"]["id"]

    # 404, not 403 — we don't leak that the ID exists at all
    res = client.get(f"/api/services/{service_id}", headers=headers_b)
    assert res.status_code == 404


def test_user_cannot_modify_or_delete_others_service(client):
    headers_a = register_and_auth(client, "a@example.com")
    headers_b = register_and_auth(client, "b@example.com")

    create = _make_service(client, headers_a, name="A's API")
    sid = create.get_json()["service"]["id"]

    assert client.patch(f"/api/services/{sid}", json={"name": "hijacked"}, headers=headers_b).status_code == 404
    assert client.delete(f"/api/services/{sid}", headers=headers_b).status_code == 404

    res = client.get(f"/api/services/{sid}", headers=headers_a)
    assert res.get_json()["service"]["name"] == "A's API"


# --- Update + delete ---

def test_partial_update_only_changes_supplied_fields(client, auth_headers):
    create = _make_service(client, auth_headers, name="old", environment="development")
    sid = create.get_json()["service"]["id"]

    res = client.patch(f"/api/services/{sid}", json={"name": "new"}, headers=auth_headers)
    assert res.status_code == 200
    service = res.get_json()["service"]
    assert service["name"] == "new"
    assert service["environment"] == "development"


def test_update_rejects_invalid_enum(client, auth_headers):
    create = _make_service(client, auth_headers)
    sid = create.get_json()["service"]["id"]

    res = client.patch(f"/api/services/{sid}", json={"provider": "WeirdCloud"}, headers=auth_headers)
    assert res.status_code == 400


def test_health_update_sets_last_checked(client, auth_headers):
    create = _make_service(client, auth_headers)
    sid = create.get_json()["service"]["id"]

    res = client.patch(f"/api/services/{sid}/health", json={
        "health_status": "healthy",
        "response_time_ms": 42,
    }, headers=auth_headers)
    assert res.status_code == 200
    service = res.get_json()["service"]
    assert service["health_status"] == "healthy"
    assert service["response_time_ms"] == 42
    assert service["last_checked_at"] is not None


def test_delete_returns_204_and_resource_is_gone(client, auth_headers):
    create = _make_service(client, auth_headers, name="doomed")
    sid = create.get_json()["service"]["id"]

    res = client.delete(f"/api/services/{sid}", headers=auth_headers)
    assert res.status_code == 204

    res = client.get(f"/api/services/{sid}", headers=auth_headers)
    assert res.status_code == 404
