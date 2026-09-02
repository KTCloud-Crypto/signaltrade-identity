import httpx

from signaltrade_identity.config import settings
from signaltrade_identity.strategy_client import disable_live_subscriptions


def test_strategy_client_sends_internal_service_token(monkeypatch):
    monkeypatch.setattr(settings, "internal_service_token", "runtime-token")

    def fake_post(url, *, headers, timeout):
        assert url.endswith("/internal/strategy/users/7/disable-live-subscriptions")
        assert headers == {"X-SignalTrade-Service-Token": "runtime-token"}
        return httpx.Response(200, request=httpx.Request("POST", url), json={"updated": 1})

    monkeypatch.setattr(httpx, "post", fake_post)
    disable_live_subscriptions(7)
