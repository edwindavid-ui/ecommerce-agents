from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_register_user_returns_user_and_token():
    payload = {
        "name": "Alice Buyer",
        "email": "alice@example.com",
        "password": "SecurePass123",
        "role": "buyer",
    }

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["user"]["email"] == "alice@example.com"
    assert body["user"]["role"] == "buyer"
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_user_with_valid_credentials():
    payload = {
        "email": "alice@example.com",
        "password": "SecurePass123",
    }

    response = client.post("/auth/login", json=payload)

    assert response.status_code == 200
    assert response.json()["user"]["email"] == "alice@example.com"
    assert "access_token" in response.json()


def test_login_rejects_invalid_password():
    payload = {
        "email": "alice@example.com",
        "password": "wrong-password",
    }

    response = client.post("/auth/login", json=payload)

    assert response.status_code == 401
