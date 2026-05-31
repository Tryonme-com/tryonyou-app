#!/usr/bin/env python3
"""
Limpieza soberana (segura): restaura firebase-applet-config.json completo.

NO inserta código en App.tsx (eso rompe TypeScript). UserCheck + initPauAlpha están en App.tsx.
NO sustituye 133 errores mágicamente: corrige dependencias con `npm install` y el código en el IDE.

Patente: PCT/EP2025/067317 — Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

from despertar_a_pau import despertar_a_pau


def limpieza_soberana_total() -> None:
    print("🧹 Restauración Firebase (JSON Web completo); App.tsx no se modifica desde este script.")
    despertar_a_pau()
    print("")
    print("👉 Errores TS/React: suele ser node_modules; en la raíz del repo:")
    print("   rm -rf node_modules && npm install && npm run build")


if __name__ == "__main__":
    limpieza_soberana_total()
