from __future__ import annotations

import json
import signal
import time
from typing import Any

from api.config import settings
from api.orchestrators.decision_engine import decide_event_flow
from api.orchestrators.execution_engine import execute_event_flow
from api.services.event_store import EventStore
from api.services.queue_service import QueueService
from api.services.redis_client import get_redis
from api.services.redis_lock import RedisLock
from api.utils.logging import get_logger

logger = get_logger("jules_worker")
_running = True
REASON_MISSING_EVENT_RECORD = "missing_event_store_record"


def _log(level: str, msg: str, **extra: Any) -> None:
    getattr(logger, level)(msg, extra=extra)


def process_once() -> bool:
    redis = get_redis()
    queue = QueueService(redis)
    store = EventStore(redis)

    queue.requeue_due_retries()
    job = queue.pop(timeout_seconds=settings.worker_pop_timeout_seconds)
    if not job:
        return False

    event_id = str(job["event_id"])
    trace_id = str(job.get("trace_id", "no-trace"))
    attempts = int(job.get("attempts", 0)) + 1
    lock = RedisLock(redis, key=f"stripe:lock:{event_id}", ttl_seconds=settings.lock_ttl_seconds)

    if not lock.acquire():
        queue.schedule_retry(event_id, trace_id, attempts)
        _log("warning", "lock_not_acquired", event_id=event_id, trace_id=trace_id, status="retry_scheduled")
        return True

    try:
        stored = store.get_event(event_id)
        if not stored:
            queue.send_to_dead_letter(event_id, trace_id, attempts, REASON_MISSING_EVENT_RECORD)
            _log("error", "missing_event_record", event_id=event_id, trace_id=trace_id, status="dead_letter")
            return True

        event = json.loads(stored.get("payload", "{}"))
        context = {"trace_id": trace_id, "attempts": attempts, "event_state": stored}
        decision = decide_event_flow(event, context)

        _log(
            "info",
            "decision_made",
            event_id=event_id,
            event_type=event.get("type", "unknown"),
            trace_id=trace_id,
            action=decision.action,
        )

        result = execute_event_flow(decision, event, context)
        store.update_status(event_id, "completed", attempts=attempts)
        _log(
            "info",
            "event_completed",
            event_id=event_id,
            event_type=event.get("type", "unknown"),
            trace_id=trace_id,
            status="completed",
            action=decision.action,
            provider=result.get("provider"),
        )
        return True
    except Exception as exc:  # noqa: BLE001
        error_text = f"{type(exc).__name__}: {exc}"
        if attempts < settings.max_retry_attempts:
            store.update_status(event_id, "retrying", attempts=attempts, error=error_text)
            queue.schedule_retry(event_id, trace_id, attempts)
            _log("warning", "event_retry", event_id=event_id, trace_id=trace_id, status="retrying")
        else:
            store.update_status(event_id, "dead_letter", attempts=attempts, error=error_text)
            queue.send_to_dead_letter(event_id, trace_id, attempts, error_text)
            _log("error", "event_dead_letter", event_id=event_id, trace_id=trace_id, status="dead_letter")
        return True
    finally:
        lock.release()


def run_forever() -> None:
    global _running

    def _stop_handler(signum: int, _: object) -> None:
        global _running
        _running = False
        _log("info", "worker_stopping", trace_id="worker", status=f"signal_{signum}")

    signal.signal(signal.SIGTERM, _stop_handler)
    signal.signal(signal.SIGINT, _stop_handler)
    _log("info", "worker_started", trace_id="worker")
    while _running:
        processed = process_once()
        if not processed:
            time.sleep(1.0)


if __name__ == "__main__":
    run_forever()
