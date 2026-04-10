"""
Auditoría de impacto matinal V10 — verificación de clearing bancario (Lafayette / LVMH).

  python3 auditoria_impacto_matinal.py

  # Envío al centinela Telegram:
  export AUDIT_SEND_TELEGRAM=1
  export TELEGRAM_BOT_TOKEN='…'   # o TELEGRAM_TOKEN
  export TELEGRAM_CHAT_ID='…'
  python3 auditoria_impacto_matinal.py

Patente: PCT/EP2025/067317
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from typing import Dict, List

SIREN_REF = "943 610 196"
CLEARING_HOUR = 9
OBJETIVO_TOTAL = 405_680.00

INGRESOS_ESPERADOS: List[Dict[str, object]] = [
    {"origen": "Lafayette", "importe": 27_500.00},
    {"origen": "LVMH", "importe": 22_500.00},
]


def check_bank_impact(*, now: datetime | None = None) -> dict:
    """Return a structured audit result for the morning bank clearing window.

    Parameters
    ----------
    now : datetime, optional
        Override for the current timestamp (useful for testing).

    Returns
    -------
    dict with keys:
        status     – human-readable status line
        clearing   – True if the clearing window has passed
        objetivo   – target total in EUR
        ingresos   – list of expected line items
        timestamp  – ISO-formatted audit time
    """
    ahora = now or datetime.now()

    clearing_done = ahora.hour >= CLEARING_HOUR

    if clearing_done:
        estado = (
            "ESTADO: Revisa tu App Bancaria AHORA. "
            "El clearing ha finalizado."
        )
    else:
        minutos_restantes = (CLEARING_HOUR - ahora.hour - 1) * 60 + (60 - ahora.minute)
        estado = (
            f"ESTADO: Faltan {minutos_restantes} minutos "
            f"para el barrido bancario de las {CLEARING_HOUR:02d}:00."
        )

    return {
        "status": estado,
        "clearing": clearing_done,
        "objetivo": OBJETIVO_TOTAL,
        "ingresos": INGRESOS_ESPERADOS,
        "timestamp": ahora.isoformat(),
    }


def formato_consola(result: dict) -> str:
    """Pretty-print the audit result for terminal / Telegram."""
    lineas = [
        "--- [AUDITORÍA DE IMPACTO MATINAL] ---",
        f"🕐 Timestamp: {result['timestamp']}",
        f"🎯 Objetivo total: {result['objetivo']:,.2f} €",
        "",
    ]
    for ing in result["ingresos"]:
        lineas.append(f"  🔎 Buscando ingreso de: {ing['importe']:,.2f} € ({ing['origen']})")

    lineas += [
        "",
        f"📊 Clearing (>= {CLEARING_HOUR:02d}:00): {'SÍ' if result['clearing'] else 'NO'}",
        result["status"],
        "",
        f"SIREN: {SIREN_REF}",
        "Patente: PCT/EP2025/067317",
        "Bajo Protocolo de Soberanía V10 - Founder: Rubén",
    ]
    return "\n".join(lineas)


def _enviar_telegram(texto: str) -> bool:
    token = (
        os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
        or os.environ.get("TELEGRAM_TOKEN", "").strip()
    )
    chat = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat:
        print(
            "❌ AUDIT_SEND_TELEGRAM=1 pero faltan token o chat_id.",
            file=sys.stderr,
        )
        return False
    try:
        import requests
    except ImportError:
        print("❌ pip install requests", file=sys.stderr)
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        r = requests.post(
            url,
            json={"chat_id": chat, "text": texto},
            timeout=30,
        )
        if r.status_code == 200:
            print("✅ Auditoría enviada a Telegram.")
            return True
        print(f"❌ Telegram HTTP {r.status_code}: {r.text[:300]}", file=sys.stderr)
    except Exception as e:
        print(f"❌ Telegram: {e}", file=sys.stderr)
    return False


def main() -> int:
    result = check_bank_impact()
    texto = formato_consola(result)
    print(texto)

    if os.environ.get("AUDIT_SEND_TELEGRAM", "").strip() in ("1", "true", "yes"):
        _enviar_telegram(texto)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
