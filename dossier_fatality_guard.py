"""Guard de Dossier Fatality para capital TryOnYou.

No confirma ingresos bancarios por inferencia: solo activa el estado fatality
con una ventana temporal concreta, flag explícito y evidencia Qonto/bancaria.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, time
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


MIN_CAPITAL_CENTS = 45_000_000
TARGET_AMOUNT_CENTS = MIN_CAPITAL_CENTS
PARIS_TZ = ZoneInfo("Europe/Paris")
VALID_SOURCES = {"qonto", "qonto_business", "bank", "bank_statement", "treasury_monitor"}


@dataclass(frozen=True)
class FatalityGuardResult:
    status: str
    active: bool
    reason: str
    amount_cents: int = 0
    source: str = ""
    reference: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "active": self.active,
            "reason": self.reason,
            "amount_cents": self.amount_cents,
            "source": self.source,
            "reference": self.reference,
        }


def _truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "y", "on", "confirmed"}


def _parse_amount_cents(raw: Any) -> int:
    if raw is None:
        return 0
    if isinstance(raw, int):
        return raw
    if isinstance(raw, float):
        return int(round(raw))
    text = str(raw).strip().replace(" ", "")
    if not text:
        return 0
    if "," in text and "." in text:
        text = text.replace(".", "").replace(",", ".")
    elif "," in text:
        text = text.replace(",", ".")
    try:
        return int(round(float(text)))
    except ValueError:
        return 0


def load_evidence(value: str | os.PathLike[str] | dict[str, Any] | None = None) -> dict[str, Any]:
    """Carga evidencia desde dict, JSON en entorno o path local.

    Variables soportadas:
      - DOSSIER_FATALITY_EVIDENCE_JSON
      - DOSSIER_FATALITY_EVIDENCE_PATH
    """
    if isinstance(value, dict):
        return value

    raw = str(value or os.environ.get("DOSSIER_FATALITY_EVIDENCE_JSON", "")).strip()
    path_value = str(os.environ.get("DOSSIER_FATALITY_EVIDENCE_PATH", "")).strip()

    if raw:
        candidate = Path(raw)
        if candidate.exists():
            return json.loads(candidate.read_text(encoding="utf-8"))
        return json.loads(raw)

    if path_value:
        return json.loads(Path(path_value).read_text(encoding="utf-8"))

    return {}


def _is_tuesday_0800(moment: datetime) -> bool:
    local = moment.astimezone(PARIS_TZ)
    return local.weekday() == 1 and local.time().replace(second=0, microsecond=0) == time(8, 0)


def evaluate_guard(
    *,
    now: datetime | None = None,
    evidence: dict[str, Any] | None = None,
    flag: str | None = None,
) -> FatalityGuardResult:
    moment = now or datetime.now(PARIS_TZ)
    if not _is_tuesday_0800(moment):
        return FatalityGuardResult(
            status="PENDING_WINDOW",
            active=False,
            reason="Dossier Fatality solo se evalúa martes a las 08:00 Europe/Paris.",
        )

    confirmation_flag = flag
    if confirmation_flag is None:
        confirmation_flag = os.environ.get("TRYONYOU_CAPITAL_450K_CONFIRMED") or os.environ.get(
            "DOSSIER_FATALITY_CONFIRM_450K"
        )
    if not _truthy(confirmation_flag):
        return FatalityGuardResult(
            status="PENDING_VALIDATION",
            active=False,
            reason="Falta flag explícito de confirmación bancaria 450k.",
        )

    proof = evidence if evidence is not None else load_evidence()
    source = str(proof.get("source", "")).strip().lower()
    reference = str(proof.get("reference", "")).strip()
    amount_cents = _parse_amount_cents(
        proof.get("amount_cents") or proof.get("capital_cents") or proof.get("amount")
    )
    currency = str(proof.get("currency", "EUR")).strip().upper()

    if source not in VALID_SOURCES:
        return FatalityGuardResult(
            status="PENDING_EVIDENCE",
            active=False,
            reason="La fuente de evidencia no es Qonto/bancaria verificable.",
            amount_cents=amount_cents,
            source=source,
            reference=reference,
        )
    if currency != "EUR" or amount_cents < MIN_CAPITAL_CENTS or not reference:
        return FatalityGuardResult(
            status="PENDING_EVIDENCE",
            active=False,
            reason="Evidencia incompleta: requiere EUR, >=450.000 EUR y referencia bancaria.",
            amount_cents=amount_cents,
            source=source,
            reference=reference,
        )

    os.environ["DOSSIER_FATALITY_ACTIVE"] = "1"
    return FatalityGuardResult(
        status="DOSSIER_FATALITY_ACTIVE",
        active=True,
        reason="Capital 450k confirmado con evidencia bancaria y ventana Oberkampf validada.",
        amount_cents=amount_cents,
        source=source,
        reference=reference,
    )


def evaluate_fatality_guard(**kwargs: Any) -> dict[str, Any]:
    return evaluate_guard(**kwargs).as_dict()


if __name__ == "__main__":
    print(json.dumps(evaluate_guard().as_dict(), ensure_ascii=False, indent=2))
