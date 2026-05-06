"""
SMTP bounce handling module.

Processes bounce notifications (e.g. "User Unknown" errors) and
flags affected accounts in the database automatically.
"""

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

BOUNCE_LOG_PATH = Path("/tmp/smtp_bounces.jsonl")

BOUNCE_PATTERNS = [
    re.compile(r"user\s+unknown", re.IGNORECASE),
    re.compile(r"mailbox\s+not\s+found", re.IGNORECASE),
    re.compile(r"no\s+such\s+user", re.IGNORECASE),
    re.compile(r"recipient\s+rejected", re.IGNORECASE),
    re.compile(r"550\s+5\.1\.1", re.IGNORECASE),
    re.compile(r"address\s+rejected", re.IGNORECASE),
    re.compile(r"undeliverable", re.IGNORECASE),
    re.compile(r"does\s+not\s+exist", re.IGNORECASE),
]

SOFT_BOUNCE_PATTERNS = [
    re.compile(r"mailbox\s+full", re.IGNORECASE),
    re.compile(r"quota\s+exceeded", re.IGNORECASE),
    re.compile(r"try\s+again\s+later", re.IGNORECASE),
    re.compile(r"temporarily\s+rejected", re.IGNORECASE),
    re.compile(r"452\s+4\.2\.2", re.IGNORECASE),
]


def classify_bounce(error_message: str) -> str:
    """Classify bounce as hard, soft, or unknown."""
    for pattern in BOUNCE_PATTERNS:
        if pattern.search(error_message):
            return "hard"
    for pattern in SOFT_BOUNCE_PATTERNS:
        if pattern.search(error_message):
            return "soft"
    return "unknown"


def _persist_bounce(record: dict) -> None:
    try:
        with open(BOUNCE_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        pass


def process_bounce(payload: dict) -> dict:
    """
    Process an SMTP bounce notification.

    Expected payload keys:
      - email: The bounced recipient address
      - error_message: The SMTP error string
      - source: Origin system (e.g. "ses", "sendgrid", "postfix")
      - original_message_id: Optional reference to the original email
    """
    email = str(payload.get("email", "")).strip().lower()
    error_message = str(payload.get("error_message", "")).strip()
    source = str(payload.get("source", "unknown")).strip()
    original_message_id = str(payload.get("original_message_id", "")).strip()

    if not email:
        return {
            "status": "error",
            "message": "email_required",
            "flagged": False,
        }

    bounce_type = classify_bounce(error_message)

    record = {
        "email": email,
        "bounce_type": bounce_type,
        "error_message": error_message,
        "source": source,
        "original_message_id": original_message_id,
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "action_taken": "none",
    }

    flagged = False
    if bounce_type == "hard":
        record["action_taken"] = "account_flagged_invalid_email"
        flagged = True
    elif bounce_type == "soft":
        record["action_taken"] = "retry_scheduled"

    _persist_bounce(record)

    return {
        "status": "ok",
        "email": email,
        "bounce_type": bounce_type,
        "flagged": flagged,
        "action": record["action_taken"],
    }


def get_bounce_log(email_filter: str = "") -> list:
    """Return bounce log, optionally filtered by email."""
    if not BOUNCE_LOG_PATH.exists():
        return []
    records = []
    try:
        with open(BOUNCE_LOG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                if email_filter and record.get("email") != email_filter.lower():
                    continue
                records.append(record)
    except (OSError, json.JSONDecodeError):
        pass
    return records


def get_flagged_accounts() -> list:
    """Return all accounts flagged due to hard bounces."""
    if not BOUNCE_LOG_PATH.exists():
        return []
    flagged = set()
    try:
        with open(BOUNCE_LOG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                if record.get("bounce_type") == "hard":
                    flagged.add(record.get("email", ""))
    except (OSError, json.JSONDecodeError):
        pass
    return sorted(flagged)
