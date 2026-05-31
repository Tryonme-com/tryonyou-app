"""Alias de elevar_autoridad_social_safe."""

from __future__ import annotations

import sys

from elevar_autoridad_social_safe import elevar_autoridad_social_safe


def elevar_autoridad_social() -> int:
    return elevar_autoridad_social_safe()


if __name__ == "__main__":
    sys.exit(elevar_autoridad_social())
