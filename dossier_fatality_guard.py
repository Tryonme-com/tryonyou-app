"""Guard seguro para activar Dossier Fatality solo con evidencia verificable.

No confirma ingresos bancarios por si mismo. La activacion requiere:
- ventana martes 08:00 en la zona configurada;
- flag explicito de tesoreria;
- evidencia JSON local con fuente Qonto/bancaria, referencia y >= 450.000 EUR.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from global_settlement_manager import (
    DEFAULT_EVIDENCE_PATH,
    DEFAULT_TARGET_AMOUNT_CENTS,
    GlobalSettlementManager,
    SettlementConfig,
)

DEFAULT_TIMEZONE = "Europe/Paris"


def _truthy_env(name: str) -> bool:
    return (os.getenv(name) or "").strip().lower() in {"1", "true", "yes", "y", "on"}


def _capital_confirmed() -> bool:
    return any(
        (os.getenv(name) or "").strip().lower() in {"1", "true", "yes", "y", "on"}
        for name in ("TRYONYOU_CAPITAL_450K_CONFIRMED", "QONTO_CAPITAL_450K_CONFIRMED")
    )


def parse_datetime(value: str) -> datetime:
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = f"{normalized[:-1]}+00:00"
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def is_activation_window(now: datetime, timezone_name: str = DEFAULT_TIMEZONE) -> bool:
    local_now = now.astimezone(ZoneInfo(timezone_name))
    return local_now.weekday() == 1 and local_now.hour == 8 and local_now.minute == 0


class DossierFatalityGuard:
    def __init__(
        self,
        *,
        evidence_path: Path = DEFAULT_EVIDENCE_PATH,
        timezone_name: str = DEFAULT_TIMEZONE,
        target_amount_cents: int = DEFAULT_TARGET_AMOUNT_CENTS,
    ) -> None:
        self.evidence_path = evidence_path
        self.timezone_name = timezone_name
        self.target_amount_cents = target_amount_cents

    def evaluate(self, now: datetime | None = None) -> dict[str, Any]:
        current = now or datetime.now(timezone.utc)
        window_ok = is_activation_window(current, self.timezone_name)
        confirmation_ok = _capital_confirmed()

        settlement = GlobalSettlementManager(
            SettlementConfig(
                target_amount_cents=self.target_amount_cents,
                evidence_path=self.evidence_path,
            )
        ).validate_global_settlement()

        active = bool(window_ok and confirmation_ok and settlement["capital_verified"])
        missing_requirements: list[str] = []
        if not window_ok:
            missing_requirements.append("outside_tuesday_0800_window")
        if not confirmation_ok:
            missing_requirements.append("confirmation_flag_missing")
        settlement_reason = str(settlement.get("reason") or "verified_qonto_or_bank_evidence")
        if not settlement["capital_verified"] and settlement_reason not in missing_requirements:
            missing_requirements.append(settlement_reason)
        if (
            settlement_reason == "confirmation_flag_missing"
            and not self.evidence_path.exists()
            and "evidence_file_missing" not in missing_requirements
        ):
            missing_requirements.append("evidence_file_missing")

        return {
            "status": "DOSSIER_FATALITY_ACTIVE" if active else "PENDING_VALIDATION",
            "active": active,
            "checked_at": current.astimezone(timezone.utc).isoformat(),
            "timezone": self.timezone_name,
            "window_ok": window_ok,
            "confirmation_ok": confirmation_ok,
            "settlement": settlement,
            "evidence": {
                "amount_cents": settlement.get("amount_cents"),
                "source": settlement.get("source"),
                "reference": settlement.get("reference"),
            },
            "reasons": missing_requirements,
            "missing_requirements": missing_requirements,
            "capital_protection": "armed" if active else "blocked_until_verified",
            "patent": "PCT/EP2025/067317",
        }


def evaluate_dossier_fatality(
    *,
    now: datetime | None = None,
    evidence_path: Path = DEFAULT_EVIDENCE_PATH,
    timezone_name: str = DEFAULT_TIMEZONE,
) -> dict[str, Any]:
    env_path = os.getenv("GLOBAL_SETTLEMENT_EVIDENCE_PATH") or os.getenv("TRYONYOU_CAPITAL_EVIDENCE_PATH")
    selected_evidence_path = Path(env_path) if env_path and evidence_path == DEFAULT_EVIDENCE_PATH else evidence_path
    return DossierFatalityGuard(
        evidence_path=selected_evidence_path,
        timezone_name=timezone_name,
    ).evaluate(now)


def main() -> int:
    parser = argparse.ArgumentParser(description="Evalua activacion segura de Dossier Fatality.")
    parser.add_argument("--now", default="", help="Datetime ISO opcional para ejecucion controlada.")
    parser.add_argument(
        "--evidence",
        default=os.getenv("GLOBAL_SETTLEMENT_EVIDENCE_PATH")
        or os.getenv("TRYONYOU_CAPITAL_EVIDENCE_PATH")
        or str(DEFAULT_EVIDENCE_PATH),
    )
    parser.add_argument("--timezone", default=DEFAULT_TIMEZONE)
    parser.add_argument("--json", action="store_true", help="Imprime JSON compacto.")
    args = parser.parse_args()

    now = parse_datetime(args.now) if args.now else None
    result = DossierFatalityGuard(
        evidence_path=Path(args.evidence),
        timezone_name=args.timezone,
    ).evaluate(now)

    print(json.dumps(result, ensure_ascii=False, indent=None if args.json else 2))
    return 0 if result["active"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
