def test_register_creates_user_and_returns_token(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Asha Rao",
            "email": "asha@example.com",
            "password": "StrongPass123",
            "role": "citizen",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["user"]["email"] == "asha@example.com"
    assert body["user"]["role"] == "citizen"
    assert body["access_token"]


def test_register_duplicate_email_rejected(client):
    payload = {
        "name": "Asha Rao",
        "email": "asha@example.com",
        "password": "StrongPass123",
        "role": "citizen",
    }
    first = client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201

    second = client.post("/api/v1/auth/register", json=payload)
    assert second.status_code == 409


def test_login_with_correct_credentials_succeeds(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Asha Rao",
            "email": "asha@example.com",
            "password": "StrongPass123",
            "role": "citizen",
        },
    )
    response = client.post(
        "/api/v1/auth/login", json={"email": "asha@example.com", "password": "StrongPass123"}
    )
    assert response.status_code == 200
    assert response.json()["access_token"]


def test_login_with_wrong_password_rejected(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Asha Rao",
            "email": "asha@example.com",
            "password": "StrongPass123",
            "role": "citizen",
        },
    )
    response = client.post(
        "/api/v1/auth/login", json={"email": "asha@example.com", "password": "WrongPassword"}
    )
    assert response.status_code == 401


def test_profile_requires_authentication(client):
    response = client.get("/api/v1/auth/profile")
    assert response.status_code == 401


def test_profile_returns_current_user(client, auth_headers):
    response = client.get("/api/v1/auth/profile", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "citizen@example.com"


def test_citizen_cannot_access_admin_only_route(client, auth_headers):
    response = client.get("/api/v1/municipality/alerts", headers=auth_headers)
    assert response.status_code == 403


def test_admin_can_access_admin_only_route(client, admin_headers):
    response = client.get("/api/v1/municipality/alerts", headers=admin_headers)
    assert response.status_code == 200
