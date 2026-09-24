from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Decision:
    action: str
    reason: str
    priority: int = 5
    requires_ai: bool = False
    provider: str | None = None
    retryable: bool = True
    max_attempts: int = 5
