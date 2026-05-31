"""Sello de sesión Master Omega: actualiza meta del vault sin sobrescribir identidad ni módulos.

No ejecuta git push. Variables sensibles: solo lectura opcional para comprobar presencia.

Patente: PCT/EP2025/067317
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VAULT = ROOT / "master_omega_vault.json"


def main() -> int:
    if not VAULT.is_file():
        print("Falta master_omega_vault.json", file=sys.stderr)
        return 1

    data = json.loads(VAULT.read_text(encoding="utf-8"))
    meta = data.setdefault("meta", {})
    meta["last_sync"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    meta.setdefault("status", "PRODUCTION_READY_MAYO_2026")

    VAULT.write_text(json.dumps(data, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")

    key_ok = bool(os.environ.get("ELEVENLABS_API_KEY", "").strip())
    print("--- MASTER OMEGA ORCHESTRATOR OK ---")
    print(f"Vault: {VAULT.resolve()}")
    print(f"meta.last_sync = {meta['last_sync']}")
    print(f"ELEVENLABS_API_KEY en sesión: {'sí' if key_ok else 'no'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
