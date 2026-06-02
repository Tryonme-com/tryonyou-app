"""
Queue service — Redis-backed event queue.

Main queue:    Redis list  (LPUSH enqueue / BRPOP dequeue — FIFO)
Delayed queue: Redis sorted set  (score = due timestamp)
Dead-letter:   Redis list  (append only — inspect manually or via dashboard)

To swap the backend (RQ, Celery, SQS, Pub/Sub) replace the body of each
public function.  The interface is intentionally thin so callers don't need
to change.
"""
from __future__ import annotations

import json
import logging
import time
from typing import Any

from config import Config
from services.redis_client import get_redis

logger = logging.getLogger(__name__)

_DELAYED_KEY = "stripe:queue:delayed"


# ── Public API ────────────────────────────────────────────────────────────────

def enqueue_event(event: dict[str, Any]) -> None:
    """Push event onto the tail of the pending queue (FIFO for workers)."""
    r = get_redis()
    r.lpush(Config.REDIS_QUEUE_KEY, json.dumps(event, default=str))
    logger.info(
        "[queue] enqueued event_type=%s event_id=%s",
        event.get("type"), event.get("id"),
    )


def dequeue_event(timeout: int = 5) -> dict[str, Any] | None:
    """
    Pop one event from the queue.

    Uses BRPOP (blocking, real Redis) or falls back to RPOP (memory stub).
    Returns None on timeout (queue empty).
    """
    r = get_redis()
    try:
        result = r.brpop(Config.REDIS_QUEUE_KEY, timeout=timeout)
        if result is None:
            return None
        _, raw = result
    except AttributeError:
        # Memory stub doesn't support BRPOP signature; use RPOP
        raw = r.rpop(Config.REDIS_QUEUE_KEY)
        if raw is None:
            return None

    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError) as exc:
        logger.error("[queue] failed to decode dequeued event: %s", exc)
        return None


def requeue_event(event: dict[str, Any], delay_seconds: float = 0) -> None:
    """
    Re-add a failed event.

    delay_seconds > 0: store in sorted set with due timestamp as score.
    delay_seconds == 0: push directly back to main queue.
    """
    if delay_seconds > 0:
        r = get_redis()
        score = time.time() + delay_seconds
        try:
            r.zadd(_DELAYED_KEY, {json.dumps(event, default=str): score})
            logger.info(
                "[queue] requeued with delay=%.0fs event_id=%s",
                delay_seconds, event.get("id"),
            )
            return
        except Exception as exc:
            logger.warning("[queue] delayed requeue failed (%s) — pushing immediately", exc)
    enqueue_event(event)


def flush_delayed_events() -> int:
    """
    Move all due delayed events to the main queue.
    Call periodically from the worker loop.
    Returns number of events moved.
    """
    r = get_redis()
    now = time.time()
    try:
        due: list[str] = r.zrangebyscore(_DELAYED_KEY, "-inf", now)
        if not due:
            return 0
        for raw in due:
            r.lpush(Config.REDIS_QUEUE_KEY, raw)
            r.zrem(_DELAYED_KEY, raw)
        logger.info("[queue] flushed %d delayed event(s) to main queue", len(due))
        return len(due)
    except Exception as exc:
        logger.warning("[queue] flush_delayed_events error: %s", exc)
        return 0


def send_to_dead_letter(event: dict[str, Any], reason: str) -> None:
    """Push an unrecoverable event to the DLQ for manual inspection."""
    r = get_redis()
    payload = json.dumps(
        {"event_id": event.get("id"), "event_type": event.get("type"), "reason": reason[:500]},
        default=str,
    )
    r.lpush(Config.REDIS_DLQ_KEY, payload)
    logger.error(
        "[queue] dead_letter event_id=%s event_type=%s reason=%.100s",
        event.get("id"), event.get("type"), reason,
    )
