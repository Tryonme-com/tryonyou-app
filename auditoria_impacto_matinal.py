"""
Auditoría de impacto matinal V10 — verificación de clearing bancario (Lafayette / LVMH).

Incluye dos flujos complementarios:
  - check_bank_impact()          → auditoría de ingresos esperados (resumen diario).
  - check_immediate_liquidity()  → monitor de liquidez SEPA en tiempo real (minuto a minuto).

  python3 auditoria_impacto_matinal.py             # auditoría completa (ambos flujos)
  python3 auditoria_impacto_matinal.py --liquidez   # solo monitor de liquidez SEPA

  # Envío al centinela Telegram:
  export AUDIT_SEND_TELEGRAM=1
  export TELEGRAM_BOT_TOKEN='…'   # o TELEGRAM_TOKEN
  export TELEGRAM_CHAT_ID='…'
  python3 auditoria_impacto_matinal.py

Patente: PCT/EP2025/067317
"""

from __future__ import annotations

import argparse
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


SEPA_SWEEP_MARGIN_MINUTES = 15


def check_immediate_liquidity(*, now: datetime | None = None) -> dict:
    """Real-time SEPA liquidity monitor relative to the 09:00 clearing window.

    Parameters
    ----------
    now : datetime, optional
        Override for the current timestamp (useful for testing).

    Returns
    -------
    dict with keys:
        status          – human-readable status line
        sweep_started   – True once the SEPA sweep hour has passed
        minutes_left    – minutes until sweep (0 when sweep_started is True)
        timestamp       – ISO-formatted monitor time
    """
    ahora = now or datetime.now()
    target_time = ahora.replace(hour=CLEARING_HOUR, minute=0, second=0, microsecond=0)

    if ahora < target_time:
        faltan = int((target_time - ahora).total_seconds() / 60)
        estado = (
            f"ESTADO: EN TRÁNSITO. Faltan {faltan} minutos "
            "para el barrido bancario SEPA."
        )
        return {
            "status": estado,
            "sweep_started": False,
            "minutes_left": faltan,
            "timestamp": ahora.isoformat(),
        }

    estado = (
        "ESTADO: BARRIDO INICIADO. "
        f"Revisa tu banca online en los próximos {SEPA_SWEEP_MARGIN_MINUTES} minutos."
    )
    return {
        "status": estado,
        "sweep_started": True,
        "minutes_left": 0,
        "timestamp": ahora.isoformat(),
    }


def formato_liquidez(result: dict) -> str:
    """Pretty-print the liquidity monitor result for terminal / Telegram."""
    lineas = [
        f"--- [MONITOR DE LIQUIDEZ: {result['timestamp']}] ---",
        "",
        result["status"],
        "",
        f"SIREN: {SIREN_REF}",
        "Patente: PCT/EP2025/067317",
        "Bajo Protocolo de Soberanía V10 - Founder: Rubén",
    ]
    return "\n".join(lineas)


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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Auditoría de impacto matinal V10 — clearing bancario Lafayette/LVMH.",
    )
    parser.add_argument(
        "--liquidez",
        action="store_true",
        help="Solo muestra el monitor de liquidez SEPA (sin auditoría completa).",
    )
    args = parser.parse_args(argv)

    bloques: list[str] = []

    if args.liquidez:
        liq = check_immediate_liquidity()
        bloques.append(formato_liquidez(liq))
    else:
        result = check_bank_impact()
        bloques.append(formato_consola(result))
        liq = check_immediate_liquidity()
        bloques.append(formato_liquidez(liq))

    texto = "\n\n".join(bloques)
    print(texto)

    if os.environ.get("AUDIT_SEND_TELEGRAM", "").strip() in ("1", "true", "yes"):
        _enviar_telegram(texto)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
