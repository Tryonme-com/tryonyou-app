"""
Lead Capture — Google Sheets primary + SQLite fallback.

Priority:
  1. Google Sheets (if ``sheets_integration`` is available and
     ``credentials.json`` exists in the repo root or a path
     given by the ``GOOGLE_CREDENTIALS_PATH`` env var).
  2. SQLite file ``Divineo_Leads_DB.sqlite`` stored under the repo root
     when the filesystem is writable, or under TMPDIR (/tmp) otherwise.

Patente: PCT/EP2025/067317
"""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── optional Sheets integration ────────────────────────────────────────────────
try:
    from sheets_integration import register_lead as _register_lead  # type: ignore[import-not-found]
    _SHEETS_AVAILABLE = True
except ImportError:
    _register_lead = None  # type: ignore[assignment]
    _SHEETS_AVAILABLE = False

_REPO_ROOT = Path(__file__).resolve().parent.parent
_DB_FILENAME = "Divineo_Leads_DB.sqlite"


def _credentials_path() -> Path | None:
    """Return the path to credentials.json if it exists, else None."""
    env_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "").strip()
    if env_path:
        p = Path(env_path)
        return p if p.is_file() else None
    default = _REPO_ROOT / "credentials.json"
    return default if default.is_file() else None


def _sqlite_db_path() -> Path:
    """Return a writable path for the SQLite database.

    Tries the repo root first; falls back to TMPDIR (/tmp) on read-only
    deployments (e.g. Vercel).
    """
    tmp_base = Path(os.getenv("TMPDIR") or "/tmp")
    candidates = [
        _REPO_ROOT / _DB_FILENAME,
        tmp_base / _DB_FILENAME,
    ]
    for path in candidates:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            # quick write-access probe
            path.touch(exist_ok=True)
            return path
        except OSError:
            continue
    # last-resort: in-memory (data won't persist but won't crash either)
    return Path(":memory:")


def _clean_optional_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _persist_sqlite(name: str | None, email: str | None, company: str | None) -> dict[str, Any]:
    """Insert a lead row into the SQLite database and return a status dict."""
    db_path = _sqlite_db_path()
    try:
        conn = sqlite3.connect(str(db_path))
        try:
            cursor = conn.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS leads "
                "(name TEXT, email TEXT, company TEXT, date TEXT)"
            )
            cursor.execute(
                "INSERT INTO leads VALUES (?, ?, ?, ?)",
                (name, email, company, datetime.now(timezone.utc).isoformat()),
            )
            conn.commit()
        finally:
            conn.close()
        return {"status": "success", "method": "sqlite_fallback", "db_path": str(db_path)}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "message": f"SQLite persistence failed: {exc}"}


def handle_lead_submission(data: dict[str, Any]) -> dict[str, Any]:
    """Persist a lead from a POST body.

    Fields accepted: ``name``, ``email``, ``company``.

    Returns a dict with at least ``"status"`` and ``"method"``.

    Priority:
      1. Google Sheets (when ``sheets_integration`` is importable and
         ``credentials.json`` is found).
      2. SQLite fallback (repo root or /tmp).
    """
    name = _clean_optional_text(data.get("name"))
    email = _clean_optional_text(data.get("email"))
    company = _clean_optional_text(data.get("company"))

    # 1. Google Sheets (optional)
    if _SHEETS_AVAILABLE and _credentials_path() is not None:
        try:
            _register_lead(name, email, company)  # type: ignore[misc]
            return {"status": "success", "method": "sheets"}
        except Exception as exc:  # noqa: BLE001
            print(f"[lead_capture] Sheets error: {exc}")

    # 2. SQLite fallback
    return _persist_sqlite(name, email, company)
