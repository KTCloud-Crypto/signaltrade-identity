from fastapi.testclient import TestClient

from signaltrade_identity.dependencies import get_current_user
from signaltrade_identity.main import app
from signaltrade_identity.models.user import User


def test_internal_auth_returns_safe_runtime_identity():
    user = User(id=7, username="runtime-user", password="secret-hash", nickname="runner",
                bot_enabled=True, execution_mode="simulated", live_trading_enabled=False)
    app.dependency_overrides[get_current_user] = lambda: user
    try:
        response = TestClient(app).get("/internal/auth/me")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json() == {
        "id": 7, "username": "runtime-user", "nickname": "runner",
        "bot_enabled": True, "execution_mode": "simulated",
        "live_trading_enabled": False,
    }
    assert "password" not in response.json()
