"""Guard soberano para Dossier Fatality.

La proteccion de capital solo se activa con tres condiciones verificables:
ventana martes 08:00, confirmacion explicita por entorno y evidencia local
bancaria/Qonto de al menos 450.000 EUR.

Patente: PCT/EP2025/067317
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from GLOBAL_SETTLEMENT_CORE import AssetSettlementManager

DEFAULT_TIMEZONE = "Europe/Paris"
DEFAULT_ACTIVATION_FILE = "dossier_fatality_activation.json"


@dataclass(frozen=True)
class FatalityDecision:
    status: str
    reason: str
    checked_at: str
    timezone: str
    activation_file: str

    @property
    def activated(self) -> bool:
        return self.status == "DOSSIER_FATALITY_ACTIVE"


def _parse_now(raw: str | None, timezone_name: str) -> datetime:
    tz = ZoneInfo(timezone_name)
    if not raw:
        return datetime.now(tz)
    value = raw.strip().replace("Z", "+00:00")
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=tz)
    return parsed.astimezone(tz)


def _in_security_window(now: datetime) -> bool:
    return now.weekday() == 1 and now.hour == 8


def _write_activation_file(path: Path, decision: FatalityDecision, settlement_status: dict[str, Any]) -> None:
    payload = {
        **asdict(decision),
        "settlement_status": settlement_status,
        "protocol": "sovereignty_v10_fatality_guard",
        "patent": "PCT/EP2025/067317",
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def evaluate_fatality_guard(
    *,
    now: datetime | None = None,
    timezone_name: str = DEFAULT_TIMEZONE,
    activation_file: str | Path = DEFAULT_ACTIVATION_FILE,
    manager: AssetSettlementManager | None = None,
) -> FatalityDecision:
    tz = ZoneInfo(timezone_name)
    checked_at = now or datetime.now(tz)
    if checked_at.tzinfo is None:
        checked_at = checked_at.replace(tzinfo=tz)
    checked_at = checked_at.astimezone(tz)
    activation_path = Path(activation_file)

    if not _in_security_window(checked_at):
        return FatalityDecision(
            status="PENDING_VALIDATION",
            reason="outside_tuesday_0800_window",
            checked_at=checked_at.isoformat(),
            timezone=timezone_name,
            activation_file=str(activation_path),
        )

    settlement_manager = manager or AssetSettlementManager()
    if not settlement_manager.execute_global_reconciliation():
        return FatalityDecision(
            status="PENDING_VALIDATION",
            reason=str(settlement_manager.last_status.get("reason", "settlement_not_verified")),
            checked_at=checked_at.isoformat(),
            timezone=timezone_name,
            activation_file=str(activation_path),
        )

    decision = FatalityDecision(
        status="DOSSIER_FATALITY_ACTIVE",
        reason="capital_verified_and_window_open",
        checked_at=checked_at.isoformat(),
        timezone=timezone_name,
        activation_file=str(activation_path),
    )
    _write_activation_file(activation_path, decision, settlement_manager.last_status)
    return decision


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evalua activacion segura de Dossier Fatality.")
    parser.add_argument("--now", help="Fecha ISO para ejecucion controlada/tests.")
    parser.add_argument("--timezone", default=os.environ.get("TRYONYOU_FATALITY_TIMEZONE", DEFAULT_TIMEZONE))
    parser.add_argument(
        "--activation-file",
        default=os.environ.get("TRYONYOU_FATALITY_ACTIVATION_FILE", DEFAULT_ACTIVATION_FILE),
    )
    parser.add_argument("--json", action="store_true", help="Imprime salida JSON.")
    args = parser.parse_args(argv)

    decision = evaluate_fatality_guard(
        now=_parse_now(args.now, args.timezone) if args.now else None,
        timezone_name=args.timezone,
        activation_file=args.activation_file,
    )
    if args.json:
        print(json.dumps(asdict(decision), indent=2, ensure_ascii=False))
    else:
        print(f"{decision.status}: {decision.reason}")
    return 0 if decision.activated else 1


if __name__ == "__main__":
    raise SystemExit(main())
