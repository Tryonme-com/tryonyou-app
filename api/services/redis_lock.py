from __future__ import annotations

import uuid
from dataclasses import dataclass

from redis import Redis


_RELEASE_LOCK_SCRIPT = """
if redis.call('get', KEYS[1]) == ARGV[1] then
  return redis.call('del', KEYS[1])
end
return 0
"""


@dataclass
class RedisLock:
    redis: Redis
    key: str
    ttl_seconds: int
    token: str = ""

    def acquire(self) -> bool:
        self.token = str(uuid.uuid4())
        return bool(self.redis.set(self.key, self.token, nx=True, ex=self.ttl_seconds))

    def release(self) -> None:
        if not self.token:
            return
        self.redis.eval(_RELEASE_LOCK_SCRIPT, 1, self.key, self.token)

    def __enter__(self) -> "RedisLock":
        if not self.acquire():
            raise RuntimeError(f"failed to acquire redis lock: {self.key}")
        return self

    def __exit__(self, *_: object) -> None:
        self.release()
