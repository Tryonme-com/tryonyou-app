"""Alias de destilar_divineo_total_safe."""

from __future__ import annotations

import sys

from destilar_divineo_total_safe import destilar_divineo_total_safe


def destilar_divineo_total() -> int:
    return destilar_divineo_total_safe()


if __name__ == "__main__":
    sys.exit(destilar_divineo_total())
