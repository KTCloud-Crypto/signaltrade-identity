from fastapi.testclient import TestClient
from redis.exceptions import ConnectionError

from signaltrade_identity.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready(monkeypatch) -> None:
    monkeypatch.setattr("signaltrade_identity.main.identity_security_state.ping", lambda: True)
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_ready_returns_503_when_redis_is_unavailable(monkeypatch) -> None:
    def unavailable() -> bool:
        raise ConnectionError("redis unavailable")

    monkeypatch.setattr("signaltrade_identity.main.identity_security_state.ping", unavailable)
    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {"detail": "dependency unavailable"}


def test_metrics_are_exposed_without_unbounded_route_labels() -> None:
    client.get("/does-not-exist/12345")
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "signaltrade_http_requests_total" in response.text
    assert 'route="unmatched"' in response.text
    assert "/does-not-exist/12345" not in response.text
