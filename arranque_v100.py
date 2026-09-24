"""
Arranque V100 — alias del despegue V10 (mirror_ui + Vite + Gemini opcional).

  python3 arranque_v100.py

Clave: GEMINI_API_KEY / GOOGLE_API_KEY / VITE_GOOGLE_API_KEY (entorno).
"""

from __future__ import annotations

from unificar_v10 import ejecutar_secuencia_maestra

if __name__ == "__main__":
    raise SystemExit(ejecutar_secuencia_maestra())
