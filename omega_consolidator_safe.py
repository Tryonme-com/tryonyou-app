"""
Omega Consolidator — regenera backend + SPA en raíz src/ (no toca index.html de Vercel).

Gobernanza (memoria de equipo TryOnYou / Divineo):

  CONSOLIDA 70 — esta capa (Agent 70 + consolidación Omega) cierra decisiones
  técnicas y de entrega: qué se versiona, qué entra al build y qué queda fuera.
  No sustituye al criterio humano: ordena el repo para que no haya “verdades”
  sueltas.

  Jules — luces, log, juicio y seguimiento (coherencia con el protocolo y el
  espíritu de marca).

  Mesas de listings — listados de soberanía, inversión y trazabilidad (Stripe,
  cap table, anclas del PCT): las decisiones que afectan a terceros solo cuentan
  si están alineadas con esas mesas y con lo consolidado aquí.

  python3 omega_consolidator_safe.py

Luego:
  pip install -r backend/requirements.txt
  uvicorn backend.omega_core:app --reload --port 8000

  npm install && npm run dev
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
        print(f"[CONSOLIDA 70 | JULES] Consolidacion: {self.status}")
        print(f"    ROOT: {self.root}")
        print("    Gobernanza: decisiones técnicas + mesas de listings (soberanía / trazabilidad).")

    def crear_directorios(self) -> None:
        print("Verificando carpetas...")
        (self.root / "backend").mkdir(parents=True, exist_ok=True)
        (self.root / "src" / "components").mkdir(parents=True, exist_ok=True)

    def inyectar_backend(self) -> None:
        print("Backend: omega_core.py (ya versionado; este paso es idempotente).")
        # El archivo real esta en backend/omega_core.py en el repo.

    def inyectar_frontend(self) -> None:
        print("Frontend: src/ + Vite en raíz (React; ya versionado).")

    def ejecutar(self) -> None:
        self.crear_directorios()
        time.sleep(0.2)
        self.inyectar_backend()
        time.sleep(0.2)
        self.inyectar_frontend()
        print("\nListo.")
        print("  API:  uvicorn backend.omega_core:app --reload --port 8000")
        print("  UI:   npm install && npm run dev")


if __name__ == "__main__":
    OmegaConsolidatorSafe().ejecutar()
