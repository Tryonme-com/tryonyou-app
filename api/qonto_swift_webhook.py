"""
Qonto SWIFT MT103 webhook handler.

Tracks inbound SWIFT transfers, validates MT103 status fields,
and reconciles them against the internal ledger (F-2026-001 reference).
"""

import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
from pathlib import Path

QONTO_WEBHOOK_SECRET = os.getenv("QONTO_WEBHOOK_SECRET", "")
RECONCILIATION_REF = "F-2026-001"
LEDGER_LOG_PATH = Path("/tmp/qonto_swift_log.jsonl")

VALID_MT103_STATUSES = frozenset([
    "ACCP",  # Accepted
    "ACTC",  # AcceptedTechnicalValidation
    "ACSP",  # AcceptedSettlementInProcess
    "ACSC",  # AcceptedSettlementCompleted
    "RJCT",  # Rejected
    "PDNG",  # Pending
])


def verify_qonto_signature(payload_bytes: bytes, signature: str) -> bool:
    if not QONTO_WEBHOOK_SECRET:
        return True
    expected = hmac.HMAC(
        key=QONTO_WEBHOOK_SECRET.encode(),
        msg=payload_bytes,
        digestmod=hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def _persist_event(event: dict) -> None:
    try:
        with open(LEDGER_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except OSError:
        pass


def process_swift_mt103(payload: dict) -> dict:
    """
    Process inbound SWIFT MT103 webhook payload from Qonto.
    Returns reconciliation result.
    """
    transaction_id = str(payload.get("transaction_id", "")).strip()
    amount = payload.get("amount")
    currency = str(payload.get("currency", "EUR")).upper()
    status = str(payload.get("status", "")).upper()
    reference = str(payload.get("reference", "")).strip()
    sender_bic = str(payload.get("sender_bic", "")).strip()
    sender_name = str(payload.get("sender_name", "")).strip()

    event = {
        "type": "swift_mt103",
        "transaction_id": transaction_id,
        "amount": amount,
        "currency": currency,
        "status": status,
        "reference": reference,
        "sender_bic": sender_bic,
        "sender_name": sender_name,
        "received_at": datetime.now(timezone.utc).isoformat(),
    }

    if status not in VALID_MT103_STATUSES:
        event["reconciliation"] = "UNKNOWN_STATUS"
        _persist_event(event)
        return {
            "status": "warning",
            "message": f"Unknown MT103 status: {status}",
            "transaction_id": transaction_id,
            "reconciled": False,
        }

    reconciled = False
    reconciliation_match = "NONE"

    if reference and RECONCILIATION_REF in reference:
        reconciled = True
        reconciliation_match = RECONCILIATION_REF

    if status in ("ACSC", "ACSP"):
        event["settlement"] = "CONFIRMED"
    elif status == "RJCT":
        event["settlement"] = "REJECTED"
    else:
        event["settlement"] = "IN_PROGRESS"

    event["reconciliation"] = reconciliation_match
    event["reconciled"] = reconciled
    _persist_event(event)

    return {
        "status": "ok",
        "transaction_id": transaction_id,
        "mt103_status": status,
        "settlement": event["settlement"],
        "reconciled": reconciled,
        "reconciliation_ref": reconciliation_match,
        "amount": amount,
        "currency": currency,
    }


def get_swift_log() -> list:
    """Return all persisted SWIFT events."""
    if not LEDGER_LOG_PATH.exists():
        return []
    events = []
    try:
        with open(LEDGER_LOG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    events.append(json.loads(line))
    except (OSError, json.JSONDecodeError):
        pass
    return events
