from fastapi.testclient import TestClient

from signaltrade_identity.config import settings
from signaltrade_identity.database import SessionLocal
from signaltrade_identity.main import app
from signaltrade_identity.models.api_key import ApiKey
from signaltrade_identity.models.user import User


def test_internal_credentials_require_token_and_return_decrypted_values(monkeypatch):
    monkeypatch.setattr(settings, "internal_service_token", "runtime-token")
    with SessionLocal() as db:
        db.add(User(id=7, username="internal-user", password="hashed",
                    nickname="Internal User"))
        db.flush()
        db.add(ApiKey(user_id=7, encrypted_access_key="encrypted-a",
                      encrypted_secret_key="encrypted-s"))
        db.commit()
    monkeypatch.setattr(
        "signaltrade_identity.api_internal.resolve_exchange_credentials",
        lambda api_key: ("access", "secret"),
    )
    client = TestClient(app)

    assert client.get("/internal/exchange-credentials/7").status_code == 401
    response = client.get(
        "/internal/exchange-credentials/7",
        headers={"X-SignalTrade-Service-Token": "runtime-token"},
    )
    assert response.status_code == 200
    assert response.json() == {"access_key": "access", "secret_key": "secret"}


def test_internal_credentials_hide_missing_key_behind_authenticated_contract(monkeypatch):
    monkeypatch.setattr(settings, "internal_service_token", "runtime-token")
    response = TestClient(app).get(
        "/internal/exchange-credentials/99",
        headers={"X-SignalTrade-Service-Token": "runtime-token"},
    )
    assert response.status_code == 404
