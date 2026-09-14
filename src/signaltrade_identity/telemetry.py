import contextvars
import time
from ipaddress import ip_address, ip_network

from fastapi import Request
from prometheus_client import Counter, Gauge, Histogram

from signaltrade_identity.config import settings

request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("request_id", default=None)
user_id_var: contextvars.ContextVar[int | None] = contextvars.ContextVar("user_id", default=None)
SECURITY_EVENTS = Counter("signaltrade_security_events_total", "Security audit events", ["event_type", "outcome"])
EXTERNAL_REQUESTS = Counter("signaltrade_external_requests_total", "External API requests", ["provider", "operation", "outcome"])
EXTERNAL_DURATION = Histogram("signaltrade_external_request_duration_seconds", "External API latency", ["provider", "operation"])
HTTP_REQUESTS = Counter("signaltrade_http_requests_total", "HTTP requests", ["method", "route", "status"])
HTTP_DURATION = Histogram("signaltrade_http_request_duration_seconds", "HTTP request latency", ["method", "route"])
HTTP_IN_PROGRESS = Gauge("signaltrade_http_requests_in_progress", "Currently running HTTP requests")
DB_POOL_CONNECTIONS = Gauge(
    "signaltrade_db_pool_connections",
    "SQLAlchemy database pool connections by state",
    ["state"],
)


def instrument_db_pool(engine) -> None:
    """Expose live QueuePool state; StaticPool used by tests has no pool counters."""
    pool = engine.pool
    metrics = {
        "size": getattr(pool, "size", None),
        "checked_in": getattr(pool, "checkedin", None),
        "checked_out": getattr(pool, "checkedout", None),
        "overflow": getattr(pool, "overflow", None),
    }
    for state, callback in metrics.items():
        if callable(callback):
            DB_POOL_CONNECTIONS.labels(state).set_function(callback)
    max_overflow = getattr(pool, "_max_overflow", None)
    if isinstance(max_overflow, int):
        DB_POOL_CONNECTIONS.labels("capacity").set_function(
            lambda: pool.size() + max(max_overflow, 0)
        )


def instrument_http(app) -> None:
    @app.middleware("http")
    async def observe_request(request: Request, call_next):
        if request.url.path == "/metrics":
            return await call_next(request)
        started = time.perf_counter()
        HTTP_IN_PROGRESS.inc()
        status = 500
        try:
            response = await call_next(request)
            status = response.status_code
            return response
        finally:
            route = getattr(request.scope.get("route"), "path", "unmatched")
            HTTP_REQUESTS.labels(request.method, route, str(status)).inc()
            HTTP_DURATION.labels(request.method, route).observe(time.perf_counter() - started)
            HTTP_IN_PROGRESS.dec()


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
