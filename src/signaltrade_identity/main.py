from fastapi import FastAPI, HTTPException
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from redis.exceptions import RedisError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from starlette.responses import Response

from signaltrade_identity.api_auth import router as auth_router
from signaltrade_identity.api_internal import auth_router as internal_auth_router, router as internal_router
from signaltrade_identity.api_users import router as users_router
from signaltrade_identity.config import settings
from signaltrade_identity.database import SessionLocal
from signaltrade_identity.redis_state import identity_security_state

app = FastAPI(
    title="SignalTrade Identity API",
    version="1.0.0",
    docs_url=None if settings.is_production else "/docs",
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_host_list)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(internal_router)
app.include_router(internal_auth_router)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready", tags=["system"])
def ready() -> dict[str, str]:
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        identity_security_state.ping()
    except (SQLAlchemyError, RedisError) as error:
        raise HTTPException(status_code=503, detail="dependency unavailable") from error
    return {"status": "ready"}


@app.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
