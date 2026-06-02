from __future__ import annotations

import json
import time
from typing import Any

from redis import Redis

from api.config import settings


class QueueService:
    def __init__(self, redis: Redis):
        self.redis = redis
        self.queue_key = settings.redis_queue_key
        self.retry_key = settings.redis_retry_key
        self.dead_letter_key = settings.redis_dead_letter_key

    def enqueue(self, event_id: str, trace_id: str, attempts: int = 0) -> None:
        self.redis.lpush(
            self.queue_key,
            json.dumps({"event_id": event_id, "trace_id": trace_id, "attempts": attempts}),
        )

    def pop(self, timeout_seconds: int = 5) -> dict[str, Any] | None:
        item = self.redis.brpop(self.queue_key, timeout=timeout_seconds)
        if not item:
            return None
        _, payload = item
        return json.loads(payload)

    def schedule_retry(self, event_id: str, trace_id: str, attempts: int) -> None:
        delay = min((2 ** max(attempts - 1, 0)) * settings.retry_backoff_base_seconds, 300)
        due_ts = int(time.time()) + delay
        value = json.dumps({"event_id": event_id, "trace_id": trace_id, "attempts": attempts})
        self.redis.zadd(self.retry_key, {value: due_ts})

    def requeue_due_retries(self) -> int:
        now = int(time.time())
        items = self.redis.zrangebyscore(self.retry_key, min="-inf", max=now)
        if not items:
            return 0
        pipe = self.redis.pipeline()
        for item in items:
            pipe.lpush(self.queue_key, item)
            pipe.zrem(self.retry_key, item)
        pipe.execute()
        return len(items)

    def send_to_dead_letter(self, event_id: str, trace_id: str, attempts: int, reason: str) -> None:
        self.redis.lpush(
            self.dead_letter_key,
            json.dumps(
                {
                    "event_id": event_id,
                    "trace_id": trace_id,
                    "attempts": attempts,
                    "reason": reason[:600],
                    "dead_lettered_at": int(time.time()),
                }
            ),
        )
