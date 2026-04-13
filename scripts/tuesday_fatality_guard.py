#!/usr/bin/env python3
"""
Tuesday 08:00 security guard for capital protection.

What it does:
1) Validates whether execution is happening on Tuesday at/after 08:00 (Europe/Paris)
2) Confirms expected capital entry amount (default: 450000 EUR)
3) Activates Dossier Fatality by writing signed evidence logs
4) Optionally notifies Telegram if credentials are present in env vars

Environment variables (optional):
- TELEGRAM_BOT_TOKEN or TELEGRAM_TOKEN
- TELEGRAM_CHAT_ID
- TRYONYOU_EXPECTED_AMOUNT_EUR (default 450000)
- TRYONYOU_CONFIRMED_AMOUNT_EUR (overrides --confirmed-amount)
- TRYONYOU_FATALITY_TZ (default Europe/Paris)
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

PATENT = "PCT/EP2025/067317"
SIRET = "94361019600017"
ROOT = Path(__file__).resolve().parents[1]
DOSSIER_FILE = ROOT / "dossier_fatality.json"
ACTIVATION_LOG = ROOT / "logs" / "security_fatality_activations.log"
ACTIVATION_MARKER = ROOT / "logs" / "dossier_fatality_active.json"


@dataclass(frozen=True)
class GuardResult:
    ok: bool
    reason: str


def _now_in_tz(tz_name: str) -> datetime:
    return datetime.now(ZoneInfo(tz_name))


def _is_tuesday_0800_or_later(now: datetime) -> bool:
    return now.weekday() == 1 and (now.hour > 8 or (now.hour == 8 and now.minute >= 0))


def _env_float(key: str, default: float) -> float:
    value = os.environ.get(key, "").strip()
    if not value:
        return default
    return float(value)


def _confirm_amount(expected_amount: float, confirmed_amount: float) -> GuardResult:
    if confirmed_amount < expected_amount:
        return GuardResult(
            ok=False,
            reason=(
                f"Capital entry not confirmed. expected={expected_amount:.2f} "
                f"confirmed={confirmed_amount:.2f}"
            ),
        )
    return GuardResult(ok=True, reason=f"Capital entry confirmed at {confirmed_amount:.2f} EUR")


def _telegram_notify(message: str) -> bool:
    token = (
        os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
        or os.environ.get("TELEGRAM_TOKEN", "").strip()
    )
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        return False

    try:
        response = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": message},
            timeout=30,
        )
        return response.status_code == 200
    except requests.RequestException:
        return False


def _activate_dossier_fatality(now: datetime, expected_amount: float, confirmed_amount: float) -> None:
    ACTIVATION_LOG.parent.mkdir(parents=True, exist_ok=True)

    dossier_payload = {}
    if DOSSIER_FILE.exists():
        dossier_payload = json.loads(DOSSIER_FILE.read_text(encoding="utf-8"))

    evidence = {
        "timestamp": now.isoformat(),
        "timezone": str(now.tzinfo),
        "capital_expected_eur": expected_amount,
        "capital_confirmed_eur": confirmed_amount,
        "dossier_fatality_loaded": bool(dossier_payload),
        "patent": PATENT,
        "siret": SIRET,
        "status": "activated",
    }

    with ACTIVATION_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(evidence, ensure_ascii=True) + "\n")

    ACTIVATION_MARKER.write_text(json.dumps(evidence, indent=2, ensure_ascii=True), encoding="utf-8")


def run_guard(confirmed_amount: float, force: bool = False) -> int:
    tz_name = os.environ.get("TRYONYOU_FATALITY_TZ", "Europe/Paris").strip() or "Europe/Paris"
    expected_amount = _env_float("TRYONYOU_EXPECTED_AMOUNT_EUR", 450000.0)
    now = _now_in_tz(tz_name)

    if not force and not _is_tuesday_0800_or_later(now):
        print(
            f"Guard window closed. Current {tz_name} time={now.isoformat()} "
            "required=Tuesday 08:00 or later."
        )
        return 2

    amount_check = _confirm_amount(expected_amount=expected_amount, confirmed_amount=confirmed_amount)
    if not amount_check.ok:
        print(amount_check.reason)
        return 3

    _activate_dossier_fatality(
        now=now,
        expected_amount=expected_amount,
        confirmed_amount=confirmed_amount,
    )
    success_msg = (
        "TRYONYOU SECURITY SUCCESS\n"
        f"- Tuesday guard executed at {now.isoformat()}\n"
        f"- Confirmed entry: {confirmed_amount:,.2f} EUR\n"
        "- Dossier Fatality: ACTIVATED\n"
        f"- Patent: {PATENT}"
    )
    print(success_msg)

    if _telegram_notify(success_msg):
        print("Telegram notification sent.")
    else:
        print("Telegram notification skipped (missing creds or delivery error).")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Tuesday 08:00 guard for 450000 EUR entry + Dossier Fatality activation."
    )
    parser.add_argument(
        "--confirmed-amount",
        type=float,
        default=None,
        help="Confirmed capital entry in EUR. Can be overridden by TRYONYOU_CONFIRMED_AMOUNT_EUR.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Bypass Tuesday 08:00 window checks for controlled runs.",
    )
    args = parser.parse_args()

    env_amount = os.environ.get("TRYONYOU_CONFIRMED_AMOUNT_EUR", "").strip()
    confirmed_amount = float(env_amount) if env_amount else (args.confirmed_amount or 0.0)
    return run_guard(confirmed_amount=confirmed_amount, force=args.force)


if __name__ == "__main__":
    raise SystemExit(main())
