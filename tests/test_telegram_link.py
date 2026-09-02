from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from signaltrade_identity.database import Base
from signaltrade_identity.models.user import User
from signaltrade_identity.telegram_link import link_telegram_chat, unlink_telegram_chat


def _session():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine, tables=[User.__table__])
    return sessionmaker(bind=engine)()


def _user(username: str, **values) -> User:
    return User(username=username, password="hashed", nickname=username, **values)


def test_valid_code_connects_chat() -> None:
    db = _session()
    user = _user(
        "link-user",
        telegram_link_code="ABCD2345",
        telegram_link_expires_at=datetime.utcnow() + timedelta(minutes=5),
    )
    db.add(user)
    db.commit()
    assert link_telegram_chat(db, " abcd2345 ", "chat-1")
    assert user.telegram_chat_id == "chat-1"
    assert user.telegram_link_code is None


def test_expired_code_is_rejected() -> None:
    db = _session()
    user = _user(
        "expired-user",
        telegram_link_code="EXPR2345",
        telegram_link_expires_at=datetime.utcnow() - timedelta(seconds=1),
    )
    db.add(user)
    db.commit()
    assert not link_telegram_chat(db, "EXPR2345", "chat-1")


def test_unlink_clears_telegram_state() -> None:
    db = _session()
    user = _user("unlink-user", telegram_chat_id="chat-1")
    db.add(user)
    db.commit()
    unlink_telegram_chat(db, user)
    assert user.telegram_chat_id is None
