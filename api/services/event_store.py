"""
Event state store — Redis-backed idempotency and lifecycle tracking.

State machine
─────────────
  RECEIVED ──► PROCESSING ──► PROCESSED
                          └──► FAILED ──► (retry) ──► PROCESSING
                                     └──► (max retries) ──► DEAD_LETTER

Redis keys
──────────
  stripe:event:{event_id}   Hash — status, type, timestamps, retry count
  stripe:lock:{event_id}    String (SET NX EX) — processing lock
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from config import Config
from services.redis_client import get_redis
from services.redis_lock import RedisLock

logger = logging.getLogger(__name__)

_EVENT_KEY = "stripe:event:{event_id}"
_LOCK_KEY = "stripe:lock:{event_id}"


class EventStatus:
    RECEIVED = "received"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"


# ── Public API ────────────────────────────────────────────────────────────────

def is_event_processed(event_id: str) -> bool:
    """Return True if the event has already been fully handled or dead-lettered."""
    meta = get_redis().hgetall(_event_key(event_id))
    return meta.get("status", "") in (EventStatus.PROCESSED, EventStatus.DEAD_LETTER)


def mark_event_received(event_id: str, metadata: dict[str, Any]) -> None:
    """Record that the webhook accepted this event. Idempotent."""
    r = get_redis()
    r.hset(
        _event_key(event_id),
        mapping={
            "status": EventStatus.RECEIVED,
            "event_type": metadata.get("type", "unknown"),
            "livemode": str(metadata.get("livemode", False)),
            "received_at": _now(),
            "retries": "0",
        },
    )
    r.expire(_event_key(event_id), Config.REDIS_EVENT_TTL)
    logger.debug("[event_store] received event_id=%s", event_id)


def mark_event_processing(event_id: str) -> bool:
    """
    Claim the event for processing.

    Uses a SET NX EX lock so that concurrent workers cannot claim the same
    event simultaneously.

    Returns True if this worker acquired the lock, False otherwise.
    """
    r = get_redis()
    with RedisLock(r, _lock_key(event_id), ttl=Config.REDIS_LOCK_TTL) as acquired:
        if not acquired:
            return False
        r.hset(
            _event_key(event_id),
            mapping={
                "status": EventStatus.PROCESSING,
                "processing_at": _now(),
            },
        )
    return True


def mark_event_processed(event_id: str) -> None:
    get_redis().hset(
        _event_key(event_id),
        mapping={
            "status": EventStatus.PROCESSED,
            "processed_at": _now(),
        },
    )
    logger.debug("[event_store] processed event_id=%s", event_id)


def mark_event_failed(event_id: str, reason: str) -> int:
    """
    Record a processing failure and increment the retry counter.
    Returns the new retry count.
    """
    r = get_redis()
    meta = r.hgetall(_event_key(event_id))
    retries = int(meta.get("retries", "0")) + 1
    r.hset(
        _event_key(event_id),
        mapping={
            "status": EventStatus.FAILED,
            "failed_at": _now(),
            "retries": str(retries),
            "last_error": reason[:500],
        },
    )
    logger.warning(
        "[event_store] failed event_id=%s retries=%d reason=%.100s",
        event_id, retries, reason,
    )
    return retries


def get_event_metadata(event_id: str) -> dict[str, Any]:
    return get_redis().hgetall(_event_key(event_id))


# ── Private helpers ───────────────────────────────────────────────────────────

def _event_key(event_id: str) -> str:
    return _EVENT_KEY.format(event_id=event_id)


def _lock_key(event_id: str) -> str:
    return _LOCK_KEY.format(event_id=event_id)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
