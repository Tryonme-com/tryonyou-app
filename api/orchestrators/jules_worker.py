"""
Jules worker — standalone async event processor.

Run this as a separate process (outside Vercel):
    PYTHONPATH=api python -m orchestrators.jules_worker

Architecture
────────────
  1. Flush any delayed-requeue events that are now due
  2. Dequeue one event (blocking BRPOP with timeout)
  3. Acquire distributed lock (skip if another worker holds it)
  4. Check idempotency (skip if already processed)
  5. decide_event_flow → Decision
  6. execute_event_flow → result
  7. On success: mark_event_processed
  8. On retryable failure: requeue with exponential backoff
  9. On non-retryable / max-retries: send_to_dead_letter

Traceability: every log line includes event_id so logs can be correlated
across decision, execution, and AI provider calls.
"""
from __future__ import annotations

import logging
import os
import signal
import sys
import time
from typing import Any

# ── Make api/ importable when run as `python -m orchestrators.jules_worker`
_api_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _api_dir not in sys.path:
    sys.path.insert(0, _api_dir)

from config import Config
from services.event_store import (
    EventStatus,
    get_event_metadata,
    is_event_processed,
    mark_event_failed,
    mark_event_processed,
    mark_event_processing,
)
from services.queue_service import (
    dequeue_event,
    flush_delayed_events,
    requeue_event,
    send_to_dead_letter,
)
from services.redis_client import get_redis
from services.redis_lock import RedisLock
from orchestrators.decision_engine import decide_event_flow
from orchestrators.execution_engine import execute_event_flow

logger = logging.getLogger(__name__)

_MAX_RETRIES = 3
_SHUTDOWN = False


def _setup_signals() -> None:
    def _handler(signum, frame):
        global _SHUTDOWN
        logger.info("[worker] shutdown signal received")
        _SHUTDOWN = True

    signal.signal(signal.SIGTERM, _handler)
    signal.signal(signal.SIGINT, _handler)


# ── Worker loop ───────────────────────────────────────────────────────────────

def run_worker() -> None:
    """Run the Jules worker loop until SIGTERM/SIGINT."""
    _setup_signals()
    logger.info("[worker] starting — queue=%s", Config.REDIS_QUEUE_KEY)

    while not _SHUTDOWN:
        try:
            _tick()
        except Exception as exc:
            logger.exception("[worker] unhandled error in tick: %s", exc)
            time.sleep(1)


def _tick() -> None:
    """One iteration: flush delayed, dequeue, process."""
    flush_delayed_events()

    event = dequeue_event(timeout=5)
    if event is None:
        return

    event_id: str = event.get("id", "")
    event_type: str = event.get("type", "")

    logger.info(
        "[worker] dequeued event_id=%s event_type=%s", event_id, event_type
    )

    # ── Idempotency check ─────────────────────────────────────────────────
    if is_event_processed(event_id):
        logger.info("[worker] duplicate event_id=%s — skipping", event_id)
        return

    # ── Distributed lock (prevents concurrent workers racing) ─────────────
    r = get_redis()
    lock_key = f"stripe:lock:{event_id}"
    with RedisLock(r, lock_key, ttl=Config.REDIS_LOCK_TTL) as acquired:
        if not acquired:
            logger.info("[worker] lock not acquired event_id=%s — skipping", event_id)
            return

        # Re-check after acquiring lock (TOCTOU guard)
        if is_event_processed(event_id):
            logger.info("[worker] duplicate (post-lock) event_id=%s — skipping", event_id)
            return

        _process_event(event)


def _process_event(event: dict[str, Any]) -> None:
    event_id = event.get("id", "")
    mark_event_processing(event_id)

    context = get_event_metadata(event_id)
    retries = int(context.get("retries", "0"))

    try:
        decision = decide_event_flow(event, context)
        result = execute_event_flow(decision, event, context)

        if result.get("ok"):
            mark_event_processed(event_id)
            logger.info(
                "[worker] done event_id=%s action=%s",
                event_id, result.get("action"),
            )
        else:
            retryable = result.get("retryable", False)
            reason = result.get("action", "execution_returned_not_ok")
            _handle_failure(event, event_id, reason, retries, retryable)

    except Exception as exc:
        logger.exception("[worker] exception event_id=%s: %s", event_id, exc)
        _handle_failure(event, event_id, str(exc)[:200], retries, retryable=True)


def _handle_failure(
    event: dict[str, Any],
    event_id: str,
    reason: str,
    retries: int,
    retryable: bool,
) -> None:
    new_retries = mark_event_failed(event_id, reason)

    if not retryable or new_retries >= _MAX_RETRIES:
        logger.error(
            "[worker] sending to DLQ event_id=%s retries=%d reason=%.100s",
            event_id, new_retries, reason,
        )
        send_to_dead_letter(event, reason)
    else:
        delay = 2 ** new_retries  # 2s, 4s, 8s
        logger.info(
            "[worker] requeuing event_id=%s retry=%d delay=%.0fs",
            event_id, new_retries, delay,
        )
        requeue_event(event, delay_seconds=delay)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL, logging.INFO),
        format="%(asctime)s %(levelname)-8s %(name)s %(message)s",
    )
    run_worker()
