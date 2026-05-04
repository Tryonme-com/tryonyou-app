"""Global Settlement Manager - auditoria segura de conciliacion TryOnYou.

Este modulo evita declarar capital como verificado sin una fuente Qonto/bancaria
trazable. La conciliacion solo queda VERIFIED con flag explicito y evidencia JSON
local suficiente; en cualquier otro caso permanece en PENDING_VALIDATION.

Patente: PCT/EP2025/067317
Bajo Protocolo de Soberania V10 - Founder: Ruben
"""

from __future__ import annotations

import argparse
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger("tryonyou.global_settlement")
DEFAULT_TARGET_AMOUNT_CENTS = 45_000_000
DEFAULT_TARGET_BALANCE_EUR = 450_000.0
DEFAULT_EVIDENCE_PATH = "capital_450k_evidence.json"
DEFAULT_AUDIT_LOG_PATH = Path("logs") / "global_settlement_audit.jsonl"
VALID_SOURCES = {"qonto", "bank", "banking", "sepa", "wire"}
CONFIRMATION_ENV_KEYS = (
    "TRYONYOU_CAPITAL_450K_CONFIRMED",
    "QONTO_450K_CONFIRMED",
    "CAPITAL_450K_CONFIRMED",
)


@dataclass(frozen=True)
class SettlementConfig:
    target_amount_cents: int = DEFAULT_TARGET_AMOUNT_CENTS
    issue_ref: str = "Issue-194"
    evidence_path: Path = Path(DEFAULT_EVIDENCE_PATH)
    audit_log_path: Path = DEFAULT_AUDIT_LOG_PATH


def _configure_logging() -> None:
    if LOGGER.handlers:
        return
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - [AUDIT] - %(message)s"))
    LOGGER.addHandler(handler)
    LOGGER.setLevel(logging.INFO)


def _truthy_env(keys: tuple[str, ...] = CONFIRMATION_ENV_KEYS) -> bool:
    return any((os.environ.get(key) or "").strip().lower() in {"1", "true", "yes"} for key in keys)


def _load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None, "evidence_file_missing"
    except OSError as exc:
        return None, f"evidence_read_error:{exc}"
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return None, f"evidence_json_error:{exc.msg}"
    if not isinstance(data, dict):
        return None, "evidence_not_object"
    return data, None


def _amount_cents(data: dict[str, Any]) -> int | None:
    raw = data.get("amount_cents")
    if raw is None and data.get("amount_eur") is not None:
        try:
            return int(round(float(str(data["amount_eur"]).replace(",", ".")) * 100))
        except (TypeError, ValueError):
            return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


class GlobalSettlementManager:
    """Valida conciliacion global con evidencias, no con logs optimistas."""

    def __init__(self, config: SettlementConfig | None = None) -> None:
        _configure_logging()
        self.config = config or SettlementConfig()

    def validate_global_settlement(self) -> dict[str, Any]:
        LOGGER.info("Iniciando protocolo de conciliacion global: %s", self.config.issue_ref)

        if not _truthy_env():
            return self._record(self._pending("confirmation_flag_missing"))

        evidence, error = _load_json(self.config.evidence_path)
        if error:
            return self._record(self._pending(error))
        assert evidence is not None

        amount = _amount_cents(evidence)
        source = str(evidence.get("source", "")).strip().lower()
        reference = str(evidence.get("reference", "")).strip()

        if amount is None:
            return self._record(self._pending("invalid_amount", evidence=evidence))
        if amount < self.config.target_amount_cents:
            return self._record(self._pending("amount_below_target", evidence=evidence, amount_cents=amount))
        if source not in VALID_SOURCES:
            return self._record(self._pending("invalid_source", evidence=evidence, amount_cents=amount))
        if not reference:
            return self._record(self._pending("missing_reference", evidence=evidence, amount_cents=amount))

        result = {
            "status": "VERIFIED",
            "issue_ref": self.config.issue_ref,
            "target_amount_cents": self.config.target_amount_cents,
            "amount_cents": amount,
            "source": source,
            "reference": reference,
            "verified_at": datetime.now(timezone.utc).isoformat(),
            "verified": True,
            "capital_verified": True,
            "protocol": "sovereignty_v10_global_settlement",
            "patent": "PCT/EP2025/067317",
        }
        LOGGER.info("[SUCCESS] Capital verificado con evidencia %s:%s", source, reference)
        return self._record(result)

    def trigger_bunker_deployment(self, settlement: dict[str, Any]) -> dict[str, Any]:
        if settlement.get("status") != "VERIFIED":
            LOGGER.info("Despliegue bunker no activado: conciliacion pendiente.")
            return {
                "status": "BLOCKED",
                "reason": "settlement_not_verified",
                "settlement_status": settlement.get("status"),
            }
        LOGGER.info("Despliegue bunker Oberkampf 75011 sincronizado. Galeria web auditada.")
        return {
            "status": "READY_TO_DEPLOY",
            "bunker": "Oberkampf 75011",
            "gallery": "web",
            "settlement_reference": settlement.get("reference"),
        }

    def _pending(
        self,
        reason: str,
        *,
        evidence: dict[str, Any] | None = None,
        amount_cents: int | None = None,
    ) -> dict[str, Any]:
        LOGGER.info("Conciliacion pendiente: %s", reason)
        payload: dict[str, Any] = {
            "status": "PENDING_VALIDATION",
            "reason": reason,
            "issue_ref": self.config.issue_ref,
            "target_amount_cents": self.config.target_amount_cents,
            "capital_verified": False,
            "verified": False,
            "protocol": "sovereignty_v10_global_settlement",
            "patent": "PCT/EP2025/067317",
        }
        if amount_cents is not None:
            payload["amount_cents"] = amount_cents
        if evidence is not None:
            payload["evidence_keys"] = sorted(str(key) for key in evidence.keys())
        return payload

    def _record(self, result: dict[str, Any]) -> dict[str, Any]:
        entry = {
            "event": "global_settlement_validation",
            "ts": datetime.now(timezone.utc).isoformat(),
            "issue_ref": self.config.issue_ref,
            "status": result.get("status"),
            "reason": result.get("reason"),
            "verified": bool(result.get("verified")),
            "amount_cents": result.get("amount_cents"),
            "target_amount_cents": self.config.target_amount_cents,
            "evidence_path": str(self.config.evidence_path),
        }
        try:
            self.config.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
            with self.config.audit_log_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except OSError as exc:
            LOGGER.warning("No se pudo escribir auditoria global settlement: %s", exc)
        return result


def run(evidence_path: str | None = None) -> dict[str, Any]:
    target_raw = (os.environ.get("GLOBAL_SETTLEMENT_TARGET_CENTS") or "").strip()
    try:
        target_amount_cents = int(target_raw) if target_raw else DEFAULT_TARGET_AMOUNT_CENTS
    except ValueError:
        target_amount_cents = DEFAULT_TARGET_AMOUNT_CENTS
    resolved_evidence = (
        evidence_path
        or os.environ.get("GLOBAL_SETTLEMENT_EVIDENCE_PATH")
        or os.environ.get("TRYONYOU_CAPITAL_EVIDENCE_PATH")
        or DEFAULT_EVIDENCE_PATH
    )
    config = SettlementConfig(
        target_amount_cents=target_amount_cents,
        evidence_path=Path(resolved_evidence),
    )
    manager = GlobalSettlementManager(config)
    settlement = manager.validate_global_settlement()
    deployment = manager.trigger_bunker_deployment(settlement)
    return {"settlement": settlement, "deployment": deployment}


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida conciliacion global TryOnYou sin ficcion financiera.")
    parser.add_argument("--evidence", default=None, help="Ruta JSON de evidencia Qonto/bancaria.")
    parser.add_argument("--json", action="store_true", help="Imprime resultado JSON.")
    args = parser.parse_args()

    result = run(args.evidence)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(result["settlement"]["status"])
    return 0 if result["settlement"]["status"] == "VERIFIED" else 3


if __name__ == "__main__":
    raise SystemExit(main())
