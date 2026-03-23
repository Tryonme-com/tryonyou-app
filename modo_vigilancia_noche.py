"""
Bucle tipo heartbeat en terminal (demo). Ctrl+C para salir.

- E50_VIGILANCIA_INTERVAL: segundos entre mensajes (por defecto 60).

No sustituye monitorización real (Stripe, Vercel, logs). python3 modo_vigilancia_noche.py
"""

from __future__ import annotations

import os
import sys
import time


def _interval() -> float:
    raw = os.environ.get("E50_VIGILANCIA_INTERVAL", "60").strip()
    try:
        return max(5.0, float(raw))
    except ValueError:
        return 60.0


def modo_vigilancia_noche() -> int:
    print("🌙 Jules: Entrando en Modo Vigilancia Nocturna...")
    print("📡 Radar enfocado en: Avenue Montaigne, Haussmann y Bpifrance.")
    print("ℹ️  Ctrl+C para salir.")

    sec = _interval()
    try:
        while True:
            time.sleep(sec)
            print("💎 Búnker seguro. Heartbeat OK.", end="\r", flush=True)
    except KeyboardInterrupt:
        print("\n✅ Vigilancia detenida. Buenos días, París.")
        return 130


if __name__ == "__main__":
    sys.exit(modo_vigilancia_noche())
