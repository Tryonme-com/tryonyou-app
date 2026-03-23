"""
Bucle de espera: cuando exista el archivo de señal, avisa y termina.

- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).
- Archivo señal: E50_PAGO_SIGNAL (por defecto pago_confirmado.txt en ROOT).
- E50_CENTINELA_INTERVAL: segundos entre comprobaciones (por defecto 10).
- E50_CENTINELA_BELL=1: emite pitidos de terminal (\\a).

No sustituye webhooks Stripe; es utilidad local de demo.

Ejecutar: python3 centinela_hambre.py
"""

from __future__ import annotations

import os
import sys
import time

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)


def _on(x: str) -> bool:
    return os.environ.get(x, "").strip().lower() in ("1", "true", "yes", "on")


def _interval() -> float:
    raw = os.environ.get("E50_CENTINELA_INTERVAL", "10").strip()
    try:
        v = float(raw)
        return max(1.0, v)
    except ValueError:
        return 10.0


def centinela_hambre() -> int:
    print("🚨 Centinela activado. Ctrl+C para salir sin señal de pago.")

    os.makedirs(ROOT, exist_ok=True)
    name = os.environ.get("E50_PAGO_SIGNAL", "pago_confirmado.txt").strip() or "pago_confirmado.txt"
    signal_path = os.path.join(ROOT, name)
    interval = _interval()

    try:
        while True:
            if os.path.isfile(signal_path):
                print("\n💰 ¡DINERO EN CAJA! (señal de archivo detectada)")
                if _on("E50_CENTINELA_BELL"):
                    for _ in range(10):
                        print("\a", end="", flush=True)
                return 0
            time.sleep(interval)
            print(
                f"📡 Vigilando… señal={name} · {interval}s",
                end="\r",
                flush=True,
            )
    except KeyboardInterrupt:
        print("\nCentinela detenido. El búnker sigue en la red.")
        return 130


if __name__ == "__main__":
    sys.exit(centinela_hambre())
