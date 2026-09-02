from sqlalchemy.orm import Session


def enqueue_notification_requested(
    db: Session,
    *,
    chat_id: str,
    message: str,
    producer: str,
    notification_type: str,
    user_id: int | None = None,
) -> None:
    """Boundary for the transactional notification outbox.

    The concrete outbox mapping is added with the HTTP API extraction. Keeping
    this function explicit prevents Identity domain code from importing the
    messaging runtime repository.
    """
    del db, chat_id, message, producer, notification_type, user_id

