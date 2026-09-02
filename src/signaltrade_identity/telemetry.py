import contextvars
from ipaddress import ip_address, ip_network

from fastapi import Request
from prometheus_client import Counter, Histogram

from signaltrade_identity.config import settings

request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("request_id", default=None)
user_id_var: contextvars.ContextVar[int | None] = contextvars.ContextVar("user_id", default=None)
SECURITY_EVENTS = Counter("signaltrade_security_events_total", "Security audit events", ["event_type", "outcome"])
EXTERNAL_REQUESTS = Counter("signaltrade_external_requests_total", "External API requests", ["provider", "operation", "outcome"])
EXTERNAL_DURATION = Histogram("signaltrade_external_request_duration_seconds", "External API latency", ["provider", "operation"])


def resolve_client_ip(request: Request) -> str | None:
    if not request.client:
        return None
    peer = request.client.host
    try:
        trusted = any(ip_address(peer) in ip_network(cidr, strict=False) for cidr in settings.trusted_proxy_cidr_list)
    except ValueError:
        trusted = False
    if trusted:
        forwarded = request.headers.get("x-forwarded-for", "").split(",", 1)[0].strip()
        if forwarded:
            try:
                return str(ip_address(forwarded))
            except ValueError:
                pass
    return peer


def log_event(logger, level: int, event: str, **fields) -> None:
    logger.log(level, event, extra={"event": event, **fields})
