"""
Simulación de progreso de build (no consulta la API de Vercel).
"""

from __future__ import annotations

import time


def monitor_vercel() -> None:
    print("📡 Monitoreando logs de Vercel...")
    steps = ["[Building]", "[Optimizing]", "[Deploying]", "[Verifying]"]
    for step in steps:
        print(f"Estado actual: {step}")
        time.sleep(3)

    print("\n💎 STATUS: LIVE (EN VERDE)")
    print("🔗 URL: tryonyou-app.vercel.app")


if __name__ == "__main__":
    monitor_vercel()
