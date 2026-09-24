"""
Evita el bucle de reprovisionado de firebase-applet-config.json.

  TRYONYOU_FIREBASE_REPROVISION=1  → permite que despertar_a_pau / forzar_llave / fix_marais escriban el JSON.

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import os
import sys


def exit_if_firebase_applet_locked(script: str) -> None:
    if os.environ.get("TRYONYOU_FIREBASE_REPROVISION", "").strip() == "1":
        return
    print(
        f"🔒 [{script}] firebase-applet-config.json sellado. "
        "Para reprovisionar: export TRYONYOU_FIREBASE_REPROVISION=1",
        file=sys.stderr,
    )
    raise SystemExit(2)
