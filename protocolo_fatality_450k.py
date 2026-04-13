#!/usr/bin/env python3
"""
Protocolo de seguridad para confirmar entrada de 450.000 EUR y activar Dossier Fatality.

- Verifica evidencia local en JSON (sin inventar confirmaciones bancarias).
- Permite modo programado para martes 08:00.
- Opcional: señal a Telegram usando variables de entorno.

Uso:
  python3 protocolo_fatality_450k.py --status
  python3 protocolo_fatality_450k.py --confirm-now --evidence-file security/evidence_450k.json
  python3 protocolo_fatality_450k.py --schedule-preview
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from urllib import error, request


ROOT = Path(__file__).resolve().parent
DOSSIER_PATH = ROOT / "dossier_fatality.json"
DEFAULT_EVIDENCE_PATH = ROOT / "security" / "evidence_450k.json"
TARGET_AMOUNT_EUR = 450_000.0
TARGET_WEEKDAY = 1  # Monday=0, Tuesday=1
TARGET_HOUR = 8
TARGET_MINUTE = 0

PATENT = "PCT/EP2025/067317"
PROTOCOL_STAMP = "Bajo Protocolo de Soberanía V10 - Founder: Rubén"
TELEGRAM_DEFAULT_HANDLE = "@tryonyou_deploy_bot"


@dataclass
class EvidenceCheck:
    ok: bool
    reason: str
    amount_eur: float
    tx_id: str | None


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"No existe: {path}")
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _validate_evidence(path: Path) -> EvidenceCheck:
    try:
        payload = _load_json(path)
    except Exception as exc:
        return EvidenceCheck(
            ok=False,
            reason=f"Evidencia inválida o ausente ({exc})",
            amount_eur=0.0,
            tx_id=None,
        )

    try:
        amount = float(payload.get("amount_eur", 0))
    except (TypeError, ValueError):
        amount = 0.0

    tx_id = payload.get("transaction_id")
    status = str(payload.get("status", "")).strip().lower()
    currency = str(payload.get("currency", "")).strip().upper()

    if currency and currency != "EUR":
        return EvidenceCheck(
            ok=False,
            reason=f"Moneda no soportada en protocolo: {currency}",
            amount_eur=amount,
            tx_id=tx_id,
        )
    if status not in {"confirmed", "settled"}:
        return EvidenceCheck(
            ok=False,
            reason="Estado de evidencia no confirmado/settled",
            amount_eur=amount,
            tx_id=tx_id,
        )
    if amount < TARGET_AMOUNT_EUR:
        return EvidenceCheck(
            ok=False,
            reason=f"Importe insuficiente: {amount:.2f} EUR",
            amount_eur=amount,
            tx_id=tx_id,
        )

    return EvidenceCheck(
        ok=True,
        reason="Evidencia validada",
        amount_eur=amount,
        tx_id=tx_id,
    )


def _next_tuesday_0800(now: datetime) -> datetime:
    days_ahead = (TARGET_WEEKDAY - now.weekday()) % 7
    candidate = now + timedelta(days=days_ahead)
    candidate = candidate.replace(
        hour=TARGET_HOUR,
        minute=TARGET_MINUTE,
        second=0,
        microsecond=0,
    )
    if candidate <= now:
        candidate += timedelta(days=7)
    return candidate


def _is_tuesday_0800_window(now: datetime) -> bool:
    if now.weekday() != TARGET_WEEKDAY:
        return False
    return now.hour == TARGET_HOUR and now.minute == TARGET_MINUTE


def _activate_dossier(activation_note: str, amount_eur: float, tx_id: str | None) -> None:
    dossier = _load_json(DOSSIER_PATH)
    dossier["fatality_activation"] = {
        "active": True,
        "activated_at": datetime.now().isoformat(timespec="seconds"),
        "note": activation_note,
        "amount_eur": amount_eur,
        "transaction_id": tx_id,
        "protocol": PROTOCOL_STAMP,
        "patent": PATENT,
    }
    DOSSIER_PATH.write_text(json.dumps(dossier, indent=4, ensure_ascii=True) + "\n", encoding="utf-8")


def _send_telegram(msg: str) -> bool:
    token = (os.environ.get("TELEGRAM_BOT_TOKEN", "") or os.environ.get("TELEGRAM_TOKEN", "")).strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    handle = os.environ.get("TELEGRAM_BOT_HANDLE", TELEGRAM_DEFAULT_HANDLE).strip() or TELEGRAM_DEFAULT_HANDLE
    if not token or not chat_id:
        return False
    text = f"{handle} {msg}"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": text}).encode("utf-8")
    req = request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=20) as resp:
            return 200 <= resp.status < 300
    except (error.URLError, TimeoutError):
        return False


def run_status(evidence_path: Path) -> int:
    now = datetime.now()
    next_slot = _next_tuesday_0800(now)
    check = _validate_evidence(evidence_path)
    print(f"[STATUS] Ahora: {now.isoformat(timespec='seconds')}")
    print(f"[STATUS] Próximo martes 08:00: {next_slot.isoformat(timespec='seconds')}")
    print(f"[STATUS] Ventana activa: {'SI' if _is_tuesday_0800_window(now) else 'NO'}")
    print(f"[STATUS] Evidencia: {'OK' if check.ok else 'PENDIENTE'} — {check.reason}")
    print(f"[STATUS] Importe detectado: {check.amount_eur:.2f} EUR")
    return 0


def run_confirm(evidence_path: Path, require_window: bool) -> int:
    now = datetime.now()
    if require_window and not _is_tuesday_0800_window(now):
        print(
            "[BLOCK] Fuera de ventana martes 08:00. "
            "Ejecuta en ventana exacta o usa --allow-outside-window.",
            file=sys.stderr,
        )
        return 2

    check = _validate_evidence(evidence_path)
    if not check.ok:
        print(f"[BLOCK] No se activa Dossier Fatality: {check.reason}", file=sys.stderr)
        return 3

    note = (
        "Entrada 450000 EUR confirmada mediante evidencia local; "
        "activación de resguardo de capital ejecutada."
    )
    _activate_dossier(note, check.amount_eur, check.tx_id)
    msg = (
        "✅ Seguridad activada: Dossier Fatality ENABLED con evidencia confirmada "
        f"({check.amount_eur:.2f} EUR). {PROTOCOL_STAMP} {PATENT}"
    )
    notified = _send_telegram(msg)
    print("[OK] Dossier Fatality activado.")
    print(f"[OK] Telegram: {'enviado' if notified else 'omitido/sin credenciales'}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Protocolo de seguridad 450k + Dossier Fatality")
    parser.add_argument("--status", action="store_true", help="Muestra estado de ventana/evidencia")
    parser.add_argument("--confirm-now", action="store_true", help="Confirma y activa ahora")
    parser.add_argument(
        "--allow-outside-window",
        action="store_true",
        help="Permite activar fuera de martes 08:00",
    )
    parser.add_argument("--schedule-preview", action="store_true", help="Muestra el próximo martes 08:00")
    parser.add_argument(
        "--evidence-file",
        default=str(DEFAULT_EVIDENCE_PATH),
        help="Ruta al JSON de evidencia de entrada",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    evidence_path = Path(args.evidence_file).resolve()

    if args.schedule_preview:
        print(_next_tuesday_0800(datetime.now()).isoformat(timespec="seconds"))
        return 0
    if args.status:
        return run_status(evidence_path)
    if args.confirm_now:
        return run_confirm(evidence_path, require_window=not args.allow_outside_window)

    print("Usa --status, --confirm-now o --schedule-preview.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
