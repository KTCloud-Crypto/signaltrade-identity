import httpx

from signaltrade_identity.config import settings
from signaltrade_identity.portfolio_client import has_open_positions


def test_portfolio_client_sends_internal_token(monkeypatch):
    monkeypatch.setattr(settings, "internal_service_token", "runtime-token")

    def fake_get(url, *, headers, timeout):
        assert url.endswith("/internal/portfolio/users/7/open-positions")
        assert headers == {"X-SignalTrade-Service-Token": "runtime-token"}
        return httpx.Response(200, request=httpx.Request("GET", url), json=[])

    monkeypatch.setattr(httpx, "get", fake_get)
    assert has_open_positions(7) is False
