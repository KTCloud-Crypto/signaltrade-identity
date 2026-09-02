"""Identity domain: authentication, exchange connection, and security."""

from signaltrade_identity.crypto import decrypt, encrypt
from signaltrade_identity.exchange_credentials import (
    ExchangeCredentialsError,
    resolve_exchange_credentials,
)
from signaltrade_identity.security import (
    JWTError,
    LoginAttemptGuard,
    SecurityEventLogger,
    SimpleRateLimiter,
    create_jwt_token,
    decode_jwt_token,
    hash_password,
    security_event_logger,
    verify_password,
)
from signaltrade_identity.telegram_link import (
    TelegramLinkCode,
    issue_telegram_link_code,
    link_telegram_chat,
    unlink_telegram_chat,
)

__all__ = [
    "decrypt", "encrypt", "ExchangeCredentialsError", "resolve_exchange_credentials",
    "JWTError", "LoginAttemptGuard", "SecurityEventLogger", "SimpleRateLimiter",
    "create_jwt_token", "decode_jwt_token", "hash_password", "security_event_logger",
    "verify_password", "TelegramLinkCode", "issue_telegram_link_code",
    "link_telegram_chat", "unlink_telegram_chat",
]
