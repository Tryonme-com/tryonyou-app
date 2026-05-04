"""Gestion de liquidacion global de activos TryOnYou.

La conciliacion solo se marca como verificada cuando existe una senal local
explicita y evidencia estructurada suficiente. No confirma ingresos bancarios
por narrativa ni por defecto.

Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

DEFAULT_SETTLEMENT_TARGET_CENTS = 45_000_000
DEFAULT_SETTLEMENT_EVIDENCE_FILE = "capital_450k_evidence.json"
CONFIRMATION_ENV_KEYS = (
    "TRYONYOU_CAPITAL_450K_CONFIRMED",
    "TRYONYOU_FUNDS_450K_CONFIRMED",
    "BUNKER_CAPITAL_ENTRY_CONFIRMED",
)
EVIDENCE_ENV_KEYS = (
    "GLOBAL_SETTLEMENT_EVIDENCE_FILE",
    "TRYONYOU_CAPITAL_450K_EVIDENCE_FILE",
    "TRYONYOU_FUNDS_450K_EVIDENCE_FILE",
)


def _env_truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "y", "on"}


def _parse_amount_cents(raw: Any) -> int | None:
    if isinstance(raw, bool) or raw is None:
        return None
    if isinstance(raw, int):
        return raw
    if isinstance(raw, float):
        return int(round(raw * 100))

    value = str(raw).strip()
    if not value:
        return None
    if value.isdigit():
        return int(value)

    normalized = value.replace(" ", "").replace("€", "").replace("EUR", "")
    if "," in normalized and "." in normalized:
        if normalized.rfind(",") > normalized.rfind("."):
            normalized = normalized.replace(".", "").replace(",", ".")
        else:
            normalized = normalized.replace(",", "")
    elif "," in normalized:
        normalized = normalized.replace(",", ".")
    try:
        return int(round(float(normalized) * 100))
    except ValueError:
        return None


@dataclass(frozen=True)
class SettlementEvidence:
    """Evidencia minima requerida para declarar una liquidacion verificada."""

    amount_cents: int
    currency: str
    source: str
    reference: str

    @classmethod
    def from_mapping(cls, payload: dict[str, Any]) -> "SettlementEvidence | None":
        amount_cents = _parse_amount_cents(
            payload.get("amount_cents")
            or payload.get("amountCents")
            or payload.get("amount_eur")
            or payload.get("amount")
        )
        currency = str(payload.get("currency") or "EUR").strip().upper()
        source = str(payload.get("source") or payload.get("provider") or "").strip()
        reference = str(payload.get("reference") or payload.get("transaction_id") or "").strip()
        if amount_cents is None:
            return None
        return cls(
            amount_cents=amount_cents,
            currency=currency,
            source=source,
            reference=reference,
        )

    def satisfies(self, target_cents: int) -> bool:
        return (
            self.currency == "EUR"
            and self.amount_cents >= target_cents
            and bool(self.source)
            and bool(self.reference)
        )


class AssetSettlementManager:
    """Gestiona la liquidacion y conciliacion del capital acumulado."""

    def __init__(
        self,
        *,
        total_target: float = 450000.00,
        target_cents: int | None = None,
        location: str = "Paris-Oberkampf",
        evidence_path: str | Path | None = None,
    ) -> None:
        self.total_target = total_target
        self.target_cents = target_cents or int(round(total_target * 100))
        self.location = location
        self.evidence_path = Path(evidence_path or self._default_evidence_path())
        self.last_status: dict[str, Any] = {
            "status": "PENDING_VALIDATION",
            "reason": "not_started",
        }

    @staticmethod
    def _default_evidence_path() -> str:
        for key in EVIDENCE_ENV_KEYS:
            raw = os.environ.get(key, "").strip()
            if raw:
                return raw
        return DEFAULT_SETTLEMENT_EVIDENCE_FILE

    @staticmethod
    def confirmation_flag_present() -> bool:
        return any(_env_truthy(key) for key in CONFIRMATION_ENV_KEYS)

    def load_evidence(self) -> SettlementEvidence | None:
        if not self.evidence_path.exists():
            return None
        try:
            payload = json.loads(self.evidence_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            logging.warning("Evidencia de liquidacion ilegible: %s", exc)
            return None
        if not isinstance(payload, dict):
            return None
        return SettlementEvidence.from_mapping(payload)

    def execute_global_reconciliation(self) -> bool:
        """
        Valida la liquidacion del capital acumulado con evidencia local.

        Retorna ``False`` si falta confirmacion de tesoreria o evidencia bancaria/Qonto.
        """
        logging.info(
            "Iniciando conciliacion global: %.2f EUR en %s",
            self.total_target,
            self.location,
        )

        if not self.confirmation_flag_present():
            self.last_status = {
                "status": "PENDING_VALIDATION",
                "reason": "missing_confirmation_flag",
                "target_cents": self.target_cents,
            }
            logging.warning("Liquidacion bloqueada: falta confirmacion explicita de tesoreria.")
            return False

        evidence = self.load_evidence()
        if evidence is None or not evidence.satisfies(self.target_cents):
            self.last_status = {
                "status": "PENDING_VALIDATION",
                "reason": "missing_or_insufficient_evidence",
                "target_cents": self.target_cents,
                "evidence_path": str(self.evidence_path),
            }
            logging.warning("Liquidacion bloqueada: evidencia bancaria/Qonto ausente o insuficiente.")
            return False

        self.last_status = {
            "status": "VERIFIED",
            "reason": "evidence_satisfied",
            "target_cents": self.target_cents,
            "amount_cents": evidence.amount_cents,
            "source": evidence.source,
            "reference": evidence.reference,
        }
        logging.info("[SUCCEEDED] Capital verificado por evidencia local estructurada.")
        return True

    def final_deployment_check(self) -> bool:
        """Confirma estabilidad de galeria solo tras liquidacion verificada."""
        if self.last_status.get("status") != "VERIFIED":
            logging.warning("Galeria no se marca sincronizada: liquidacion pendiente.")
            return False
        logging.info("Galeria y activos de produccion sincronizados.")
        return True


def main() -> int:
    manager = AssetSettlementManager()
    if manager.execute_global_reconciliation() and manager.final_deployment_check():
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
