from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError

from signaltrade_identity import LoginAttemptGuard, SimpleRateLimiter
from signaltrade_identity.redis_state import RedisSecurityState
from signaltrade_identity.schemas.auth import SignupRequest


class SharedFakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, int] = {}

    def eval(self, script, key_count, key, ttl):
        del script, key_count, ttl
        self.values[key] = self.values.get(key, 0) + 1
        return self.values[key]

    def get(self, key):
        return self.values.get(key)

    def delete(self, key):
        self.values.pop(key, None)


def test_login_guard_locks_and_releases() -> None:
    guard = LoginAttemptGuard(max_failures=2, lockout_minutes=5)
    now = datetime(2024, 1, 1, 12, 0, 0)
    guard.record_failure("alice", now=now)
    guard.record_failure("alice", now=now)
    assert guard.is_locked("alice", now=now)
    assert guard.allow("alice", now=now + timedelta(minutes=6))


def test_security_state_is_shared_between_replicas() -> None:
    redis = SharedFakeRedis()
    first = SimpleRateLimiter(max_requests=2, state=RedisSecurityState(redis))
    second = SimpleRateLimiter(max_requests=2, state=RedisSecurityState(redis))
    assert first.allow("client")
    assert second.allow("client")
    assert not first.allow("client")


def test_signup_requires_complete_exchange_key_pair() -> None:
    with pytest.raises(ValidationError):
        SignupRequest(
            username="paper_user",
            password="Password1",
            nickname="모의투자",
            access_key="access-key-value",
        )

