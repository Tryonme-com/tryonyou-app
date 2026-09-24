"""Renovación interactiva de GOOGLE_STUDIO_API_KEY y ejecución de oraculo_studio.py.

La clave solo vive en memoria del proceso (y en el entorno heredado al hijo).
El sellado git lo hace oraculo_studio.py (decision_estudio.json), no este script.

Push forzado: solo si ORACLE_GIT_PUSH_FORCE=1 (rama actual, --force-with-lease).
Omitir git: ORACLE_SKIP_GIT=1

Patente: PCT/EP2025/067317
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> int:
    print("\n--- RENOVACIÓN DE CLAVE: Oráculo Studio (Gemini) ---\n")

    nueva_key = input("Pega la nueva API key de Google AI Studio: ").strip()
    if not nueva_key:
        print("Error: clave vacía.", file=sys.stderr)
        return 1
    if not nueva_key.startswith("AIza"):
        print(
            "Aviso: las claves típicas empiezan por 'AIza'. "
            "Si usas otro formato, cancela y exporta la variable manualmente.",
            file=sys.stderr,
        )
        confirm = input("¿Continuar de todos modos? [s/N]: ").strip().lower()
        if confirm not in ("s", "sí", "si", "y", "yes"):
            return 1

    env = os.environ.copy()
    env["GOOGLE_STUDIO_API_KEY"] = nueva_key

    print("Consultando oraculo_studio.py (git lo gestiona el oráculo si no hay ORACLE_SKIP_GIT=1)...")
    r = subprocess.run(
        [sys.executable, str(ROOT / "oraculo_studio.py")],
        cwd=ROOT,
        env=env,
        text=True,
    )
    if r.returncode == 0:
        print("\n--- Oráculo completado con código 0 (revisa decision_estudio.json / git). ---\n")
    else:
        print(f"\n--- oraculo_studio.py terminó con código {r.returncode}. ---\n", file=sys.stderr)
    return r.returncode


if __name__ == "__main__":
    raise SystemExit(main())
