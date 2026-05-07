#!/usr/bin/env python3
"""Guard seguro para Dossier Fatality y entrada de capital 450K.

No consulta Qonto ni Stripe por si solo y nunca confirma fondos reales sin:
- ventana martes 08:00 Europe/Paris,
- flag explicito TRYONYOU_CAPITAL_450K_CONFIRMED,
- evidencia JSON local con importe EUR y referencia bancaria/Qonto.

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberania V10 - Founder: Ruben
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping
from zoneinfo import ZoneInfo

PARIS_TZ = ZoneInfo("Europe/Paris")
EXPECTED_AMOUNT_CENTS = 45_000_000
TRUTHY = {"1", "true", "yes", "y", "si", "oui", "ok", "confirmed", "confirmado"}


@dataclass(frozen=True)
class FatalityDecision:
    status: str
    active: bool
    reasons: list[str]
    expected_amount_cents: int
    checked_at_paris: str
    evidence_summary: dict[str, Any]


def _truthy(raw: str | None) -> bool:
    return (raw or "").strip().lower() in TRUTHY


def _parse_now(raw: str | None) -> datetime:
    if not raw:
        return datetime.now(PARIS_TZ)
    normalized = raw.strip().replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=PARIS_TZ)
    return parsed.astimezone(PARIS_TZ)


def _is_tuesday_0800_paris(moment: datetime) -> bool:
    paris = moment.astimezone(PARIS_TZ)
    return paris.weekday() == 1 and paris.hour == 8 and paris.minute == 0


def _amount_cents(evidence: Mapping[str, Any]) -> int | None:
    raw_cents = evidence.get("amount_cents") or evidence.get("amountCents")
    if raw_cents is not None:
        try:
            return int(raw_cents)
        except (TypeError, ValueError):
            return None

    raw_eur = evidence.get("amount_eur") or evidence.get("amount") or evidence.get("amountEUR")
    if raw_eur is None:
        return None
    try:
        return int(round(float(str(raw_eur).replace(",", ".")) * 100))
    except (TypeError, ValueError):
        return None


def _read_evidence(path: str | None) -> tuple[dict[str, Any] | None, str | None]:
    if not path:
        return None, "missing_evidence_path"
    evidence_path = Path(path).expanduser()
    if not evidence_path.is_file():
        return None, "evidence_file_not_found"
    try:
        payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None, "evidence_json_unreadable"
    if not isinstance(payload, dict):
        return None, "evidence_json_not_object"
    return payload, None


def evaluate_dossier_fatality(
    env: Mapping[str, str] | None = None,
    *,
    now: datetime | None = None,
) -> FatalityDecision:
    env = env or os.environ
    moment = now.astimezone(PARIS_TZ) if now else _parse_now(env.get("DOSSIER_FATALITY_NOW"))
    expected = int(env.get("DOSSIER_FATALITY_EXPECTED_AMOUNT_CENTS") or EXPECTED_AMOUNT_CENTS)
    reasons: list[str] = []
    evidence_summary: dict[str, Any] = {}

    if not _is_tuesday_0800_paris(moment):
        reasons.append("outside_tuesday_0800_europe_paris")

    if not _truthy(env.get("TRYONYOU_CAPITAL_450K_CONFIRMED")):
        reasons.append("missing_explicit_capital_confirmation_flag")

    evidence, evidence_error = _read_evidence(env.get("DOSSIER_FATALITY_EVIDENCE_PATH"))
    if evidence_error:
        reasons.append(evidence_error)
    elif evidence is not None:
        amount = _amount_cents(evidence)
        currency = str(evidence.get("currency") or "").upper()
        reference = (
            evidence.get("reference")
            or evidence.get("transaction_id")
            or evidence.get("qonto_transaction_id")
            or evidence.get("bank_reference")
            or ""
        )
        source = str(evidence.get("source") or evidence.get("provider") or "")
        evidence_summary = {
            "amount_cents": amount,
            "currency": currency,
            "has_reference": bool(str(reference).strip()),
            "source": source[:80],
        }
        if amount is None:
            reasons.append("missing_evidence_amount_cents")
        elif amount < expected:
            reasons.append("evidence_amount_below_450k_eur")
        if currency != "EUR":
            reasons.append("evidence_currency_not_eur")
        if not str(reference).strip():
            reasons.append("missing_bank_or_qonto_reference")

    active = not reasons
    return FatalityDecision(
        status="DOSSIER_FATALITY_ACTIVE" if active else "PENDING_VALIDATION",
        active=active,
        reasons=reasons,
        expected_amount_cents=expected,
        checked_at_paris=moment.isoformat(timespec="seconds"),
        evidence_summary=evidence_summary,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Valida activacion segura del Dossier Fatality.")
    parser.add_argument("--strict", action="store_true", help="Devuelve codigo 1 si el dossier no esta activo.")
    parser.add_argument("--status-path", help="Ruta opcional para escribir el resultado JSON.")
    args = parser.parse_args(argv)

    decision = evaluate_dossier_fatality()
    payload = asdict(decision)
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    print(text)

    if args.status_path:
        path = Path(args.status_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text + "\n", encoding="utf-8")

    if args.strict and not decision.active:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
