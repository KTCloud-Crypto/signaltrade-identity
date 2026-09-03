from fastapi.testclient import TestClient

from signaltrade_identity.config import settings
from signaltrade_identity.database import SessionLocal
from signaltrade_identity.main import app
from signaltrade_identity.models.user import User


def test_internal_telegram_user_lookup_is_protected_and_minimal(monkeypatch):
    monkeypatch.setattr(settings, "internal_service_token", "test-service-token")
    with SessionLocal() as db:
        db.add(User(username="telegram-user", password="hash", nickname="Telegram",
                    telegram_chat_id="chat-7"))
        db.commit()
    client = TestClient(app)
    assert client.get("/internal/telegram-users/chat-7").status_code == 401
    response = client.get("/internal/telegram-users/chat-7", headers={
        "X-SignalTrade-Service-Token": "test-service-token"})
    assert response.status_code == 200
    assert response.json()["username"] == "telegram-user"
    assert set(response.json()) == {"id", "username"}
