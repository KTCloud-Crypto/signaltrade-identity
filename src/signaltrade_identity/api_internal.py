import hmac

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from signaltrade_identity.database import get_db
from signaltrade_identity.config import settings
from signaltrade_identity.exchange_credentials import (
    ExchangeCredentialsError,
    resolve_exchange_credentials,
)
from signaltrade_identity.models.api_key import ApiKey
from signaltrade_identity.telegram_link import link_telegram_chat
from signaltrade_identity.dependencies import get_current_user
from signaltrade_identity.models.user import User


auth_router = APIRouter(prefix="/internal/auth", tags=["Identity Internal"])
credentials_router = APIRouter(
    prefix="/internal/exchange-credentials", tags=["Identity Internal"]
)
def require_internal_service_token(
    service_token: str | None = Header(default=None, alias="X-SignalTrade-Service-Token"),
) -> None:
    expected = settings.internal_service_token
    if not expected or not service_token or not hmac.compare_digest(service_token, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="유효한 내부 서비스 토큰이 필요합니다.")


# Defined after the dependency function so FastAPI can bind it normally.
router = APIRouter(
    prefix="/internal/telegram-links", tags=["Identity Internal"],
    dependencies=[Depends(require_internal_service_token)],
)
telegram_users_router = APIRouter(
    prefix="/internal/telegram-users", tags=["Identity Internal"],
    dependencies=[Depends(require_internal_service_token)],
)


class TelegramLinkRequest(BaseModel):
    code: str
    chat_id: str


class TelegramLinkResponse(BaseModel):
    linked: bool


class TelegramUserResponse(BaseModel):
    id: int
    username: str


@telegram_users_router.get("/{chat_id}", response_model=TelegramUserResponse)
def get_telegram_user(chat_id: str, db: Session = Depends(get_db)) -> TelegramUserResponse:
    user = db.query(User).filter(User.telegram_chat_id == chat_id).one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="연결된 SignalTrade 계정이 없습니다.")
    return TelegramUserResponse(id=user.id, username=user.username)


@router.post("", response_model=TelegramLinkResponse)
def link_telegram_account(
    payload: TelegramLinkRequest,
    db: Session = Depends(get_db),
) -> TelegramLinkResponse:
    """Notification worker 전용 Telegram 연결 command입니다.

    이 endpoint는 Compose 내부 network에서만 사용하며, 사용자/연결 코드 WRITE는
    Identity 서비스 안의 application service가 수행합니다.
    """
    return TelegramLinkResponse(
        linked=link_telegram_chat(db, payload.code, payload.chat_id),
    )


class AuthenticatedUser(BaseModel):
    id: int
    username: str
    nickname: str
    bot_enabled: bool
    execution_mode: str
    live_trading_enabled: bool


@auth_router.get("/me", response_model=AuthenticatedUser)
def authenticate_internal_user(
    current_user: User = Depends(get_current_user),
) -> AuthenticatedUser:
    """Validate a bearer token and expose only runtime authorization fields."""
    return AuthenticatedUser.model_validate(current_user, from_attributes=True)


class ExchangeCredentialsResponse(BaseModel):
    access_key: str
    secret_key: str


@credentials_router.get(
    "/{user_id}",
    response_model=ExchangeCredentialsResponse,
    dependencies=[Depends(require_internal_service_token)],
)
def get_exchange_credentials(
    user_id: int,
    db: Session = Depends(get_db),
) -> ExchangeCredentialsResponse:
    """Return decrypted credentials only to an authenticated internal runtime."""
    api_key = db.query(ApiKey).filter(ApiKey.user_id == user_id).one_or_none()
    try:
        access_key, secret_key = resolve_exchange_credentials(api_key)
    except ExchangeCredentialsError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return ExchangeCredentialsResponse(access_key=access_key, secret_key=secret_key)
