"""
Agenda de seguridad V10 — verificación martes 08:00 + activación Dossier Fatality (operativa).

Este script NO inventa ingresos ni conecta a bancos por defecto.
Solo confirma el estado con evidencia disponible en entorno/archivo y emite notificación.

Uso:
  python3 seguridad_martes_0800.py --run-now
  python3 seguridad_martes_0800.py --check-only

Variables opcionales:
  TELEGRAM_BOT_TOKEN / TELEGRAM_TOKEN
  TELEGRAM_CHAT_ID
  DOSSIER_FATALITY_PATH (default: dossier_fatality.json)

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

TARGET_WEEKDAY = 1  # Tuesday
TARGET_HOUR = 8
TARGET_MINUTE = 0
TARGET_AMOUNT_EUR = 450_000.0

BOT_TOKEN_DEFAULT = "8788913760:AAE2gS0M8v1_S96H9Fm8I-K1U9Z_6-R-K48"
CHAT_ID_DEFAULT = "7868120279"


@dataclass
class PaymentEvidence:
    confirmed: bool
    amount: float | None
    source: str
    details: str


def _parse_amount(value: str | None) -> float | None:
    if not value:
        return None
    cleaned = value.replace("€", "").replace(" ", "").replace(",", "")
    try:
        return float(cleaned)
    except ValueError:
        return None


def _read_env_evidence() -> PaymentEvidence:
    status = os.getenv("CAPITAL_450K_STATUS", "").strip().lower()
    amount = _parse_amount(os.getenv("CAPITAL_450K_AMOUNT_EUR", ""))
    source = os.getenv("CAPITAL_450K_SOURCE", "ENV") or "ENV"

    if status in {"confirmed", "ok", "received"} and amount is not None and amount >= TARGET_AMOUNT_EUR:
        return PaymentEvidence(True, amount, source, "confirmado por variables de entorno")

    details = "sin confirmación explícita en entorno"
    if status:
        details = f"estado='{status}'"
    return PaymentEvidence(False, amount, source, details)


def _load_dossier(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _activate_dossier(path: Path, evidence: PaymentEvidence) -> None:
    payload = _load_dossier(path)
    payload["dossier_fatality_state"] = "ACTIVE"
    payload["capital_protection"] = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "policy": "Dossier Fatality",
        "amount_reference_eur": TARGET_AMOUNT_EUR,
        "evidence": {
            "confirmed": evidence.confirmed,
            "amount": evidence.amount,
            "source": evidence.source,
            "details": evidence.details,
        },
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "
", encoding="utf-8")


def _is_tuesday_0800(now: datetime) -> bool:
    return (
        now.weekday() == TARGET_WEEKDAY
        and now.hour == TARGET_HOUR
        and now.minute == TARGET_MINUTE
    )


def _notify(message: str) -> None:
    token = (
        os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        or os.getenv("TELEGRAM_TOKEN", "").strip()
        or BOT_TOKEN_DEFAULT
    )
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip() or CHAT_ID_DEFAULT
    if not token or not chat_id:
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    body = json.dumps({"chat_id": chat_id, "text": message}).encode("utf-8")

    try:
        from urllib.request import Request, urlopen

        req = Request(url, data=body, headers={"Content-Type": "application/json"})
        with urlopen(req, timeout=20):
            pass
    except Exception:
        # Notificación best-effort: no bloquea flujo principal.
        pass


def main() -> int:
    parser = argparse.ArgumentParser(description="Chequeo soberano martes 08:00")
    parser.add_argument("--run-now", action="store_true", help="Ejecutar sin validar hora objetivo")
    parser.add_argument("--check-only", action="store_true", help="Solo evaluar estado, sin activar dossier")
    args = parser.parse_args()

    now = datetime.now()
    if not args.run_now and not _is_tuesday_0800(now):
        print("Fuera de ventana martes 08:00; no se ejecuta activación.")
        return 0

    evidence = _read_env_evidence()

    dossier_path = Path(os.getenv("DOSSIER_FATALITY_PATH", "dossier_fatality.json"))
    if not args.check_only:
        _activate_dossier(dossier_path, evidence)

    if evidence.confirmed:
        msg = (
            f"✅ Capital {TARGET_AMOUNT_EUR:,.0f}€ confirmado. "
            f"Dossier Fatality {'activado' if not args.check_only else 'en modo check'} "
            f"({evidence.source})."
        )
        print(msg)
        _notify(msg)
        return 0

    msg = (
        "⚠️ Capital 450.000€ no confirmado con evidencia suficiente. "
        f"Estado: {evidence.details}. "
        f"Dossier Fatality {'actualizado' if not args.check_only else 'no modificado (check-only)'} para protección preventiva."
    )
    print(msg)
    _notify(msg)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
