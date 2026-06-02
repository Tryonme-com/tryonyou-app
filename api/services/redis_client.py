"""
Redis connection singleton with in-memory fallback.

The in-memory stub covers all methods used by this project and is safe for
single-process dev/test.  It is NOT suitable for multi-process or production
deployments — set REDIS_URL to a real Redis instance for those.
"""
from __future__ import annotations

import json
import logging
import threading
from typing import Any

logger = logging.getLogger(__name__)

_client = None
_client_lock = threading.Lock()


def get_redis():
    """Return the cached Redis client (or in-memory stub)."""
    global _client
    if _client is None:
        with _client_lock:
            if _client is None:
                _client = _build_client()
    return _client


def _build_client():
    from config import Config

    if not Config.REDIS_URL:
        logger.warning(
            "[redis] REDIS_URL not set — using in-memory fallback (NOT for production)"
        )
        return _MemoryRedis()

    try:
        import redis as _lib

        client = _lib.from_url(
            Config.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
        client.ping()
        # Log only the host, never the password
        safe_url = Config.REDIS_URL.split("@")[-1]
        logger.info("[redis] connected host=%s", safe_url)
        return client
    except Exception as exc:
        logger.error(
            "[redis] connection failed (%s) — falling back to in-memory stub", exc
        )
        return _MemoryRedis()


# ── In-memory stub ────────────────────────────────────────────────────────────

class _MemoryRedis:
    """
    Minimal thread-safe in-memory Redis substitute.
    Covers: SET/GET/DEL, HSET/HGETALL, LPUSH/RPOP, EXPIRE.
    BRPOP falls back to RPOP (non-blocking).
    Sorted-set commands (ZADD/ZRANGEBYSCORE/ZREM) are no-ops that return [].
    """

    def __init__(self) -> None:
        self._kv: dict[str, str] = {}
        self._hashes: dict[str, dict[str, str]] = {}
        self._lists: dict[str, list[str]] = {}
        self._lock = threading.Lock()

    def ping(self) -> bool:
        return True

    # ── string ops ──────────────────────────────────────────────────────────

    def set(self, key: str, value: str, ex: int | None = None, nx: bool = False):
        with self._lock:
            if nx and key in self._kv:
                return None
            self._kv[key] = value
            return True

    def get(self, key: str) -> str | None:
        return self._kv.get(key)

    def delete(self, *keys: str) -> int:
        count = 0
        with self._lock:
            for k in keys:
                if self._kv.pop(k, None) is not None:
                    count += 1
        return count

    def expire(self, key: str, seconds: int) -> int:
        return 1  # not enforced

    # ── hash ops ────────────────────────────────────────────────────────────

    def hset(self, key: str, mapping: dict[str, str]) -> int:
        with self._lock:
            bucket = self._hashes.setdefault(key, {})
            bucket.update(mapping)
            return len(mapping)

    def hgetall(self, key: str) -> dict[str, str]:
        return dict(self._hashes.get(key, {}))

    # ── list ops ────────────────────────────────────────────────────────────

    def lpush(self, key: str, *values: str) -> int:
        with self._lock:
            lst = self._lists.setdefault(key, [])
            for v in reversed(values):
                lst.insert(0, v)
            return len(lst)

    def rpop(self, key: str) -> str | None:
        with self._lock:
            lst = self._lists.get(key, [])
            return lst.pop() if lst else None

    def brpop(self, key: str, timeout: int = 0):
        val = self.rpop(key)
        return (key, val) if val is not None else None

    def llen(self, key: str) -> int:
        return len(self._lists.get(key, []))

    # ── sorted-set stubs (no-ops for delayed queue) ──────────────────────────

    def zadd(self, key: str, mapping: dict) -> int:
        return 0

    def zrangebyscore(self, key: str, min_score, max_score) -> list:
        return []

    def zrem(self, key: str, *members) -> int:
        return 0
