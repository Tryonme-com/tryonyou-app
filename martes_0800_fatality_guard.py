#!/usr/bin/env python3
"""
Tuesday 08:00 security protocol for TryOnYou.

- Confirms expected capital entry (default 450000 EUR).
- Activates Dossier Fatality status when capital is confirmed.
- Emits a machine-readable status file for downstream automations.
- Sends Telegram success notifications using environment credentials.

No secrets are hardcoded in this file.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from urllib import parse, request
from zoneinfo import ZoneInfo

DEFAULT_EXPECTED_AMOUNT_EUR = 450000.0
DEFAULT_PAYOUT_FILE = ".emergency_payout"
DEFAULT_DOSSIER_FILE = "dossier_fatality.json"
DEFAULT_STATUS_FILE = "logs/dossier_fatality_tuesday_0800.json"
DEFAULT_TIMEZONE = "Europe/Paris"


def parse_amount(raw: str | None, default: float) -> float:
    if raw is None:
        return default
    cleaned = raw.strip().replace(",", ".")
    if not cleaned:
        return default
    try:
        return float(cleaned)
    except ValueError:
        return default


def load_expected_amount(payout_file: str) -> float:
    path = Path(payout_file)
    if not path.is_file():
        return DEFAULT_EXPECTED_AMOUNT_EUR
    for line in path.read_text(encoding="utf-8").splitlines():
        entry = line.strip()
        if not entry or entry.startswith("#") or "=" not in entry:
            continue
        key, value = entry.split("=", 1)
        if key.strip() == "AMOUNT":
            return parse_amount(value, DEFAULT_EXPECTED_AMOUNT_EUR)
    return DEFAULT_EXPECTED_AMOUNT_EUR


def is_tuesday_0800_window(now_local: datetime, window_minutes: int = 10) -> bool:
    if now_local.weekday() != 1:  # Monday=0, Tuesday=1
        return False
    return now_local.hour == 8 and 0 <= now_local.minute < max(1, window_minutes)


def resolve_confirmed_capital(
    expected_amount: float,
    env: Mapping[str, str],
) -> tuple[bool, str, float | None]:
    candidate_vars = (
        "SECURITY_CONFIRMED_CAPITAL_EUR",
        "CONFIRMED_CAPITAL_EUR",
        "QONTO_BALANCE_EUR",
    )
    best_source = ""
    best_value: float | None = None

    for var_name in candidate_vars:
        raw_value = env.get(var_name)
        if raw_value is None:
            continue
        value = parse_amount(raw_value, default=-1.0)
        if value < 0:
            continue
        if best_value is None or value > best_value:
            best_source = var_name
            best_value = value
        if value + 1e-9 >= expected_amount:
            return True, var_name, value

    return False, best_source, best_value


def load_dossier(dossier_file: str) -> Any:
    path = Path(dossier_file)
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"error": f"invalid_json:{path.name}"}


def write_status_file(path: str, payload: dict[str, Any]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def send_success_notification(report: Mapping[str, Any], env: Mapping[str, str]) -> bool:
    token = (
        env.get("TRYONYOU_DEPLOY_BOT_TOKEN", "").strip()
        or env.get("TELEGRAM_BOT_TOKEN", "").strip()
        or env.get("TELEGRAM_TOKEN", "").strip()
    )
    chat_id = (
        env.get("TRYONYOU_DEPLOY_CHAT_ID", "").strip()
        or env.get("TELEGRAM_CHAT_ID", "").strip()
    )
    if not token or not chat_id:
        return False

    text = (
        "Supercommit_Max success\n"
        f"Node: Oberkampf 75011\n"
        f"Expected capital: {report['expected_amount_eur']:.2f} EUR\n"
        f"Confirmed source: {report.get('confirmed_source') or 'none'}\n"
        "Dossier Fatality: ACTIVATED"
    )
    body = parse.urlencode(
        {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
        }
    ).encode("utf-8")
    req = request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=body,
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=20) as response:
            return 200 <= response.status < 300
    except Exception:
        return False


def run_protocol(
    *,
    now_local: datetime,
    expected_amount: float,
    dossier_payload: Any,
    force_run: bool,
    env: Mapping[str, str],
    window_minutes: int,
) -> tuple[dict[str, Any], int]:
    in_window = force_run or is_tuesday_0800_window(now_local, window_minutes=window_minutes)
    confirmed, source, observed = resolve_confirmed_capital(expected_amount, env)

    activated = bool(in_window and confirmed)
    state = "activated" if activated else ("outside_window" if not in_window else "awaiting_capital")
    exit_code = 0 if state in ("activated", "outside_window") else 2

    report = {
        "protocol": "tuesday_0800_dossier_fatality",
        "timezone": str(now_local.tzinfo),
        "checked_at_local": now_local.isoformat(timespec="seconds"),
        "checked_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "expected_amount_eur": expected_amount,
        "in_security_window": in_window,
        "capital_confirmed": confirmed,
        "confirmed_source": source,
        "observed_amount_eur": observed,
        "dossier_fatality_state": state,
        "dossier_fatality_activated": activated,
        "dossier_reference": dossier_payload,
        "patent": "PCT/EP2025/067317",
    }
    return report, exit_code


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Tuesday 08:00 capital check + Dossier Fatality.")
    parser.add_argument("--force-run", action="store_true", help="Run even outside Tuesday 08:00.")
    parser.add_argument("--timezone", default=DEFAULT_TIMEZONE, help="Timezone for schedule checks.")
    parser.add_argument(
        "--window-minutes",
        type=int,
        default=10,
        help="Allowed minute window after 08:00.",
    )
    parser.add_argument("--payout-file", default=DEFAULT_PAYOUT_FILE, help="Path to payout config file.")
    parser.add_argument("--dossier-file", default=DEFAULT_DOSSIER_FILE, help="Path to dossier json file.")
    parser.add_argument("--status-file", default=DEFAULT_STATUS_FILE, help="Output status file path.")
    parser.add_argument(
        "--no-notify",
        action="store_true",
        help="Do not send Telegram notification on success.",
    )
    args = parser.parse_args(argv)

    now_local = datetime.now(ZoneInfo(args.timezone))
    expected_amount = load_expected_amount(args.payout_file)
    dossier_payload = load_dossier(args.dossier_file)
    env_map = dict(os.environ)

    report, exit_code = run_protocol(
        now_local=now_local,
        expected_amount=expected_amount,
        dossier_payload=dossier_payload,
        force_run=args.force_run,
        env=env_map,
        window_minutes=max(1, args.window_minutes),
    )
    if report["dossier_fatality_activated"] and not args.no_notify:
        report["notification_sent"] = send_success_notification(report, env_map)
    else:
        report["notification_sent"] = False

    write_status_file(args.status_file, report)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
