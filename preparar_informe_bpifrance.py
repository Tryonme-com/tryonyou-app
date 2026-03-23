"""Alias de preparar_informe_bpifrance_safe."""

from __future__ import annotations

import sys

from preparar_informe_bpifrance_safe import preparar_informe_bpifrance_safe


def preparar_informe_bpifrance() -> int:
    return preparar_informe_bpifrance_safe()


if __name__ == "__main__":
    sys.exit(preparar_informe_bpifrance())
