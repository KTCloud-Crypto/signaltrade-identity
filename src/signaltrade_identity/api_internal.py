from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from signaltrade_identity.database import get_db
from signaltrade_identity.telegram_link import link_telegram_chat
from signaltrade_identity.dependencies import get_current_user
from signaltrade_identity.models.user import User


router = APIRouter(prefix="/internal/telegram-links", tags=["Identity Internal"])
auth_router = APIRouter(prefix="/internal/auth", tags=["Identity Internal"])


class TelegramLinkRequest(BaseModel):
    code: str
    chat_id: str


class TelegramLinkResponse(BaseModel):
    linked: bool


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
