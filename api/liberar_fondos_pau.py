"""Délégation Divineo V7 — exécute ``update_net_liquidity.py`` à la racine du dépôt."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]


def ejecutar_orquestacion_financiera() -> int:
    return subprocess.call(
        [sys.executable, str(_ROOT / "update_net_liquidity.py")],
        cwd=str(_ROOT),
    )


if __name__ == "__main__":
    raise SystemExit(ejecutar_orquestacion_financiera())
