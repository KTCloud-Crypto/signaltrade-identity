from sqlalchemy.orm import Session
from datetime import datetime, timezone
from uuid import uuid4

from signaltrade_identity.models.message_outbox import MessageOutbox


def enqueue_notification_requested(
    db: Session,
    *,
    chat_id: str,
    message: str,
    producer: str,
    notification_type: str,
    user_id: int | None = None,
    idempotency_key: str | None = None,
) -> bool:
    """Record a notification request in the producer's DB transaction."""
    if not chat_id:
        return False
    message_id = uuid4()
    db.add(MessageOutbox(
        message_id=str(message_id),
        message_type="NotificationRequested",
        correlation_id=str(message_id),
        producer=producer,
        schema_version=1,
        idempotency_key=idempotency_key,
        occurred_at=datetime.now(timezone.utc),
        payload={
            "chat_id": str(chat_id), "message": message,
            "notification_type": notification_type, "user_id": user_id,
        },
    ))
    return True
