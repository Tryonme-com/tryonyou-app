"""
Reporte matutino V10 para orquestación tipo Jules V7 (cron 09:00 CET).

  export TELEGRAM_BOT_TOKEN='…'
  export TELEGRAM_CHAT_ID='…'
  # opcional: sin envío (solo consola)
  export SKIP_TELEGRAM=1

  python3 reporte_diario_soberania_v10.py

Patente: PCT/EP2025/067317 | SIRET ref.: 94361019600017
"""

from __future__ import annotations

import os
import sys
from datetime import datetime

SIREN_REF = "943 610 196"
NETO_REF = "98.000,00"


def _mensaje_liquidacion(dias_restantes: int) -> str:
    fecha_hito = datetime(2026, 5, 9).date()

    if dias_restantes > 0:
        return (
            f"⏳ *MONITOR DE LIQUIDACIÓN V10*\n\n"
            f"Faltan *{dias_restantes} días* para el hito LVMH.\n"
            f"Estado: contrato certificado (SIREN {SIREN_REF}).\n"
            f"Capital en ruta: *{NETO_REF} € NETOS*."
        )
    if dias_restantes == 0:
        return (
            "💰 --- *[HITO ALCANZADO: SOBERANÍA TOTAL]* ---\n\n"
            f"✅ SIREN *{SIREN_REF}*\n"
            f"💵 *{NETO_REF} €* netos (referencia operativa).\n"
            "🎉 ¡Vívelo! BOOM. 💥"
        )
    return (
        "⏳ *MONITOR DE LIQUIDACIÓN V10*\n\n"
        f"Fecha objetivo superada ({fecha_hito}); "
        "revisar estado en sistemas contables reales."
    )


def reporte_diario_soberania() -> str:
    fecha_objetivo = datetime(2026, 5, 9)
    hoy = datetime.now()
    dias_restantes = (fecha_objetivo.date() - hoy.date()).days
    return _mensaje_liquidacion(dias_restantes)


def enviar_al_centinela(titulo: str, mensaje: str) -> bool:
    token = (
        os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
        or os.environ.get("TELEGRAM_TOKEN", "").strip()
    )
    chat = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat:
        print(
            "❌ Falta TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID.",
            file=sys.stderr,
        )
        return False
    try:
        import requests
    except ImportError:
        print("❌ pip install requests", file=sys.stderr)
        return False

    texto = f"*{titulo}*\n\n{mensaje}"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        r = requests.post(
            url,
            json={
                "chat_id": chat,
                "text": texto,
                "parse_mode": "Markdown",
            },
            timeout=30,
        )
        if r.status_code == 200:
            return True
        print(f"❌ Telegram HTTP {r.status_code}: {r.text[:400]}", file=sys.stderr)
    except Exception as e:
        print(f"❌ Telegram: {e}", file=sys.stderr)
    return False


def main() -> int:
    mensaje = reporte_diario_soberania()
    print(mensaje.replace("*", ""))

    if os.environ.get("SKIP_TELEGRAM", "").strip() in ("1", "true", "yes"):
        print("ℹ️  SKIP_TELEGRAM=1 — sin envío al centinela.")
        return 0

    if enviar_al_centinela("REPORTE MATUTINO", mensaje):
        print("✅ Centinela notificado.")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
