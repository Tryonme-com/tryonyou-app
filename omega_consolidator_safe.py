"""
Omega Consolidator — regenera backend + mirror_ui (no toca index.html de Vercel).

La UI vive en mirror_ui/ para no chocar con el despliegue Python actual.

  python3 omega_consolidator_safe.py

Luego:
  pip install -r backend/requirements.txt
  uvicorn backend.omega_core:app --reload --port 8000

  cd mirror_ui && npm install && npm run dev
"""

from __future__ import annotations

import os
import time
from pathlib import Path


def _root() -> Path:
    return Path(os.environ.get("E50_PROJECT_ROOT", os.getcwd())).resolve()


class OmegaConsolidatorSafe:
    def __init__(self) -> None:
        self.status = "V10.5 OMEGA STEALTH"
        self.root = _root()
        print(f"[JULES / AGENT 70] Consolidacion: {self.status}")
        print(f"    ROOT: {self.root}")

    def crear_directorios(self) -> None:
        print("Verificando carpetas...")
        (self.root / "backend").mkdir(parents=True, exist_ok=True)
        (self.root / "mirror_ui" / "src" / "components").mkdir(parents=True, exist_ok=True)

    def inyectar_backend(self) -> None:
        print("Backend: omega_core.py (ya versionado; este paso es idempotente).")
        # El archivo real esta en backend/omega_core.py en el repo.

    def inyectar_frontend(self) -> None:
        print("Frontend: mirror_ui/ (Vite + React; ya versionado).")

    def ejecutar(self) -> None:
        self.crear_directorios()
        time.sleep(0.2)
        self.inyectar_backend()
        time.sleep(0.2)
        self.inyectar_frontend()
        print("\nListo.")
        print("  API:  uvicorn backend.omega_core:app --reload --port 8000")
        print("  UI:   cd mirror_ui && npm install && npm run dev")


if __name__ == "__main__":
    OmegaConsolidatorSafe().ejecutar()
