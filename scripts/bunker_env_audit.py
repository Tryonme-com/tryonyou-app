"""
Auditoría rápida de presencia de variables críticas (sin volcar secretos).

Uso: python3 scripts/bunker_env_audit.py

Patente: PCT/EP2025/067317 — Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""

from __future__ import annotations

import os

keys = ["STRIPE_SECRET_KEY", "VERCEL_TOKEN"]


def main() -> None:
    print("--- AUDITORÍA DE SEGURIDAD DEL BÚNKER ---")
    for key in keys:
        raw = os.getenv(key)
        value = (raw or "").strip()
        if value:
            # Solo primeros 4 caracteres: confirma presencia sin exponer la clave
            print(f"Llave {key}: CONFIGURADA (Inicia con: {value[:4]}...)")
        else:
            print(f"Llave {key}: ¡NO DETECTADA! (Manus necesita configurarla)")
    print("------------------------------------------")


if __name__ == "__main__":
    main()
