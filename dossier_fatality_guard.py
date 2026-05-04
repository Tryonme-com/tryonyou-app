"""
Guardia del Dossier Fatality para capital TryOnYou.

No confirma entradas bancarias por narrativa. Solo activa el dossier si coinciden:
- ventana martes 08:00 Europe/Paris,
- confirmación explícita en entorno,
- evidencia JSON verificable >= 450.000 EUR.

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

CAPITAL_TARGET_CENTS = 45_000_000
ACTIVATION_AMOUNT_CENTS = CAPITAL_TARGET_CENTS
DEFAULT_TZ = "Europe/Paris"
ALLOWED_SOURCES = {"qonto", "bank", "stripe", "treasury_monitor", "financial_guard"}


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}


def is_activation_window(now: datetime | None = None, env: dict[str, str] | None = None) -> bool:
    env_map = os.environ if env is None else env
    tz = ZoneInfo(env_map.get("DOSSIER_FATALITY_TZ", DEFAULT_TZ))
    local_now = (now or datetime.now(tz)).astimezone(tz)
    return local_now.weekday() == 1 and local_now.hour == 8


def load_evidence(raw: str | None = None, env: dict[str, str] | None = None) -> dict[str, Any]:
    env_map = os.environ if env is None else env
    candidate = (raw if raw is not None else env_map.get("DOSSIER_FATALITY_EVIDENCE_JSON") or "").strip()
    if not candidate:
        path = (env_map.get("DOSSIER_FATALITY_EVIDENCE_PATH") or "").strip()
        if not path:
            return {}
        candidate = Path(path).read_text(encoding="utf-8")
    elif not candidate.startswith(("{", "[")):
        candidate = Path(candidate).read_text(encoding="utf-8")
    data = json.loads(candidate)
    if not isinstance(data, dict):
        raise ValueError("evidence_must_be_json_object")
    return data


def _amount_cents(evidence: dict[str, Any]) -> int:
    raw_cents = evidence.get("amount_cents")
    if raw_cents is not None:
        return int(raw_cents)
    raw_eur = evidence.get("amount_eur")
    if raw_eur is None:
        return 0
    return int(round(float(str(raw_eur).replace(",", ".")) * 100))


def evaluate_guard(
    *,
    now: datetime | None = None,
    env: dict[str, str] | None = None,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    env_map = os.environ if env is None else env
    explicit_confirm = _truthy(env_map.get("TRYONYOU_CAPITAL_450K_CONFIRMED")) or _truthy(
        env_map.get("DOSSIER_FATALITY_CONFIRM")
    )
    in_window = is_activation_window(now, env=env_map)
    evidence = evidence if evidence is not None else load_evidence(env=env_map)
    amount_cents = _amount_cents(evidence)
    source = str(evidence.get("source") or "").strip().lower()
    reference = str(evidence.get("reference") or evidence.get("transaction_id") or "").strip()
    currency = str(evidence.get("currency") or "EUR").strip().upper()

    evidence_ok = (
        amount_cents >= CAPITAL_TARGET_CENTS
        and currency == "EUR"
        and source in ALLOWED_SOURCES
        and bool(reference)
    )
    reasons: list[str] = []
    if not explicit_confirm:
        reasons.append("missing_confirmation_flag")
    if not in_window:
        reasons.append("outside_tuesday_0800_paris_window")
    if amount_cents < CAPITAL_TARGET_CENTS:
        reasons.append("insufficient_amount_cents")
    if currency != "EUR":
        reasons.append("invalid_currency")
    if source not in ALLOWED_SOURCES:
        reasons.append("invalid_source")
    if not reference:
        reasons.append("missing_reference")

    active = explicit_confirm and in_window and evidence_ok
    return {
        "status": "DOSSIER_FATALITY_ACTIVE" if active else "PENDING_VALIDATION",
        "active": active,
        "reasons": reasons,
        "target_amount_cents": CAPITAL_TARGET_CENTS,
        "amount_cents": amount_cents,
        "currency": currency,
        "source": source or None,
        "reference_present": bool(reference),
        "explicit_confirm": explicit_confirm,
        "activation_window": in_window,
        "evidence_ok": evidence_ok,
        "message": (
            "Capital verificado con evidencia suficiente; Dossier Fatality activo."
            if active
            else "Sin confirmación bancaria completa: no se activa ni se afirma entrada real."
        ),
    }


def evaluate_fatality_guard(**kwargs: Any) -> dict[str, Any]:
    return evaluate_guard(**kwargs)


def main() -> int:
    try:
        result = evaluate_guard()
    except Exception as exc:
        result = {
            "status": "PENDING_VALIDATION",
            "active": False,
            "error": str(exc),
            "message": "Evidencia inválida; no se activa el Dossier Fatality.",
        }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("active") else 1


if __name__ == "__main__":
    raise SystemExit(main())
