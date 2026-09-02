from signaltrade_identity.database import SessionLocal
from signaltrade_identity.models.message_outbox import MessageOutbox
from signaltrade_identity.notification_adapter import enqueue_notification_requested


def test_notification_is_recorded_in_producer_transaction() -> None:
    with SessionLocal() as db:
        created = enqueue_notification_requested(
            db,
            chat_id="chat-1",
            message="hello",
            producer="identity-api",
            notification_type="security_alert",
            user_id=7,
        )
        assert created is True
        db.flush()
        assert db.query(MessageOutbox).count() == 1
        row = db.query(MessageOutbox).one()
        assert row.status == "pending"
        assert row.message_type == "NotificationRequested"
        assert row.payload["user_id"] == 7

        db.rollback()
