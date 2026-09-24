"""
Crea la carpeta de adjuntos para envío Bpifrance (referencia operativa).

  python3 preparar_envio_bpifrance_v10.py

  # Carpeta alternativa:
  export BPIFRANCE_ENVIO_DIR=/ruta/absoluta/mi_dossier

Verifica siempre el correo y el procedimiento oficial en mon.bpifrance.fr / tu gestor.

Patente: PCT/EP2025/067317
"""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_DIR = ROOT / "Bpifrance_Envio_Urgente"


def preparar_envio_final() -> Path:
    print("📂 Agente 46: preparando carpeta de adjuntos…")
    raw = os.environ.get("BPIFRANCE_ENVIO_DIR", "").strip()
    dest = Path(raw).resolve() if raw else DEFAULT_DIR
    dest.mkdir(parents=True, exist_ok=True)
    print(f"✅ Carpeta: {dest}")
    print("📍 1. Avis de situation SIRENE (PDF u oficial).")
    print("📍 2. Factura proforma / note d’innovation (p. ej. operacion_rescate/).")
    print("📍 3. Comprueba el destinatario con Bpifrance antes de enviar (no uses un correo no verificado).")
    return dest


if __name__ == "__main__":
    preparar_envio_final()
