"""Alias de preparar_asalto_station_f_safe. Uso: E50_GIT_PUSH=1 python3 preparar_asalto_station_f.py"""

from __future__ import annotations

import sys

from preparar_asalto_station_f_safe import preparar_asalto_station_f_safe


def preparar_asalto_station_f() -> int:
    """Misma lógica que preparar_asalto_station_f_safe (sin git add . ni push --force ciego)."""
    return preparar_asalto_station_f_safe()


if __name__ == "__main__":
    sys.exit(preparar_asalto_station_f())
