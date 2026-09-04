from fastapi.testclient import TestClient

from signaltrade_identity.config import settings
from signaltrade_identity.main import app

client = TestClient(app)


def test_signup_login_and_profile_round_trip() -> None:
    signup = client.post(
        "/auth/signup",
        json={"username": "identity_user", "password": "Password1", "nickname": "사용자"},
    )
    assert signup.status_code == 201, signup.text
    assert signup.json()["username"] == "identity_user"

    login = client.post(
        "/auth/login",
        json={"username": "identity_user", "password": "Password1"},
    )
    assert login.status_code == 200, login.text
    token = login.json()["token"]["access_token"]

    profile = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert profile.status_code == 200, profile.text
    assert profile.json()["nickname"] == "사용자"
    assert profile.json()["has_api_key"] is False


def test_internal_telegram_link_requires_service_token(monkeypatch) -> None:
    monkeypatch.setattr(settings, "internal_service_token", "runtime-token")

    response = client.post(
        "/internal/telegram-links",
        json={"code": "NONE2345", "chat_id": "chat-1"},
    )

    assert response.status_code == 401


def test_internal_telegram_link_rejects_unknown_code(monkeypatch) -> None:
    monkeypatch.setattr(settings, "internal_service_token", "runtime-token")

    response = client.post(
        "/internal/telegram-links",
        json={"code": "NONE2345", "chat_id": "chat-1"},
        headers={"X-SignalTrade-Service-Token": "runtime-token"},
    )
    assert response.status_code == 200
    assert response.json() == {"linked": False}
