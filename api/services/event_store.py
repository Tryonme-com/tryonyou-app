from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from redis import Redis

from api.config import settings


class EventStore:
    def __init__(self, redis: Redis):
        self.redis = redis

    @staticmethod
    def event_key(event_id: str) -> str:
        return f"stripe:event:{event_id}"

    @staticmethod
    def idempotency_key(event_id: str) -> str:
        return f"stripe:idempotency:{event_id}"

    def mark_received_once(self, event_id: str) -> bool:
        return bool(
            self.redis.set(self.idempotency_key(event_id), "1", nx=True, ex=settings.event_ttl_seconds)
        )

    def persist_received_event(self, event: dict[str, Any], trace_id: str) -> None:
        event_id = event["id"]
        self.redis.hset(
            self.event_key(event_id),
            mapping={
                "event_id": event_id,
                "event_type": event.get("type", "unknown"),
                "payload": json.dumps(event),
                "trace_id": trace_id,
                "status": "received",
                "attempts": "0",
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        self.redis.expire(self.event_key(event_id), settings.event_ttl_seconds)

    def get_event(self, event_id: str) -> dict[str, str]:
        return self.redis.hgetall(self.event_key(event_id))

    def update_status(self, event_id: str, status: str, attempts: int | None = None, error: str | None = None) -> None:
        mapping: dict[str, str] = {
            "status": status,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        if attempts is not None:
            mapping["attempts"] = str(attempts)
        if error:
            mapping["last_error"] = error[:600]
        self.redis.hset(self.event_key(event_id), mapping=mapping)
        self.redis.expire(self.event_key(event_id), settings.event_ttl_seconds)
