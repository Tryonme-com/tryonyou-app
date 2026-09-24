"""
Arranque unidad de producción V10 — alias de unificar_v10.py.

Clave solo por entorno: GEMINI_API_KEY, GOOGLE_API_KEY o VITE_GOOGLE_API_KEY.
Nunca pegues la clave en el repo.

  python3 arranque_unidad_produccion.py
"""

from __future__ import annotations

from unificar_v10 import arranque_unidad_produccion

if __name__ == "__main__":
    raise SystemExit(arranque_unidad_produccion())
