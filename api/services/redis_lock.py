"""
Distributed lock using Redis SET NX EX.

Guarantees at most one worker processes a given event at a time.
The lock is released automatically when the context manager exits, or expires
after `ttl` seconds if the process crashes mid-execution.

Usage:
    from services.redis_lock import RedisLock, LockNotAcquiredError

    r = get_redis()
    with RedisLock(r, f"stripe:lock:{event_id}", ttl=30) as acquired:
        if not acquired:
            return  # another worker has it
        ... do work ...
"""
from __future__ import annotations

import logging
import uuid

logger = logging.getLogger(__name__)


class LockNotAcquiredError(Exception):
    """Raised when a lock cannot be acquired (already held by another worker)."""


class RedisLock:
    def __init__(self, redis_client, key: str, ttl: int = 30) -> None:
        self._r = redis_client
        self._key = key
        self._ttl = ttl
        self._token = str(uuid.uuid4())
        self._acquired = False

    def __enter__(self) -> bool:
        result = self._r.set(self._key, self._token, ex=self._ttl, nx=True)
        self._acquired = result is not None
        if not self._acquired:
            logger.debug("[redis_lock] not acquired key=%s", self._key)
        return self._acquired

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if not self._acquired:
            return
        # Only release if we still own the token — prevents releasing another
        # worker's lock if our TTL expired while we were working.
        try:
            current = self._r.get(self._key)
            if str(current) == self._token:
                self._r.delete(self._key)
        except Exception as exc:
            logger.warning("[redis_lock] release error key=%s: %s", self._key, exc)
