from __future__ import annotations

import json
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


def _log(level: str, msg: str, **extra: Any) -> None:
    getattr(logger, level)(msg, extra=extra)


def process_once() -> bool:
    redis = get_redis()
    queue = QueueService(redis)
    store = EventStore(redis)

    queue.requeue_due_retries()
    job = queue.pop(timeout_seconds=2)
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
            queue.send_to_dead_letter(event_id, trace_id, attempts, "missing_event_store_record")
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
        _log("info", "event_completed", event_id=event_id, event_type=event.get("type", "unknown"), trace_id=trace_id, status="completed")
        return True
    except Exception as exc:  # noqa: BLE001
        if attempts < settings.max_retry_attempts:
            store.update_status(event_id, "retrying", attempts=attempts, error=str(exc))
            queue.schedule_retry(event_id, trace_id, attempts)
            _log("warning", "event_retry", event_id=event_id, trace_id=trace_id, status="retrying")
        else:
            store.update_status(event_id, "dead_letter", attempts=attempts, error=str(exc))
            queue.send_to_dead_letter(event_id, trace_id, attempts, str(exc))
            _log("error", "event_dead_letter", event_id=event_id, trace_id=trace_id, status="dead_letter")
        return True
    finally:
        lock.release()


def run_forever() -> None:
    _log("info", "worker_started", trace_id="worker")
    while True:
        processed = process_once()
        if not processed:
            time.sleep(1.0)


if __name__ == "__main__":
    run_forever()
