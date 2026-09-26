from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AIProvider(ABC):
    @abstractmethod
    def run_task(self, task_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
