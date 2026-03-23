"""Alias de genesis_consolidacion_total_safe."""

from __future__ import annotations

import sys

from genesis_consolidacion_total_safe import genesis_consolidacion_total_safe


def genesis_consolidacion_total() -> int:
    return genesis_consolidacion_total_safe()


if __name__ == "__main__":
    sys.exit(genesis_consolidacion_total())
