"""Tests for api/lead_capture.py — Sheets primary + SQLite fallback."""
from __future__ import annotations

import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import api.lead_capture as lc


class TestHandleLeadSubmissionSQLite(unittest.TestCase):
    """handle_lead_submission writes to SQLite when Sheets is not configured."""

    def setUp(self) -> None:
        self.tmpdir = tempfile.mkdtemp()
        self._orig_tmpdir = os.environ.get("TMPDIR")
        os.environ["TMPDIR"] = self.tmpdir
        # Force all DB writes into self.tmpdir by masking the repo root
        self._root_patcher = patch.object(lc, "_REPO_ROOT", Path(self.tmpdir))
        self._root_patcher.start()

    def tearDown(self) -> None:
        self._root_patcher.stop()
        if self._orig_tmpdir is None:
            os.environ.pop("TMPDIR", None)
        else:
            os.environ["TMPDIR"] = self._orig_tmpdir

    def _call(self, data: dict) -> dict:
        # Ensure Sheets integration is disabled for these tests
        with patch.object(lc, "_SHEETS_AVAILABLE", False):
            return lc.handle_lead_submission(data)

    def test_sqlite_success_returns_correct_status(self) -> None:
        result = self._call({"name": "Alice", "email": "alice@example.com", "company": "ACME"})
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["method"], "sqlite_fallback")

    def test_sqlite_stores_name_email_company(self) -> None:
        self._call({"name": "Bob", "email": "bob@test.com", "company": "Corp"})
        db_path = Path(self.tmpdir) / lc._DB_FILENAME
        conn = sqlite3.connect(str(db_path))
        try:
            row = conn.execute("SELECT name, email, company FROM leads").fetchone()
        finally:
            conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "Bob")
        self.assertEqual(row[1], "bob@test.com")
        self.assertEqual(row[2], "Corp")
    def test_missing_fields_stored_as_none(self) -> None:
        result = self._call({})
        self.assertEqual(result["status"], "success")
        db_path = Path(self.tmpdir) / lc._DB_FILENAME
        conn = sqlite3.connect(str(db_path))
        try:
            row = conn.execute("SELECT name, email, company FROM leads").fetchone()
        finally:
            conn.close()
        self.assertIsNone(row[0])
        self.assertIsNone(row[1])
        self.assertIsNone(row[2])

    def test_multiple_leads_accumulate(self) -> None:
        for i in range(3):
            self._call({"name": f"User{i}", "email": f"u{i}@x.com", "company": "X"})
        db_path = Path(self.tmpdir) / lc._DB_FILENAME
        conn = sqlite3.connect(str(db_path))
        try:
            count = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
        finally:
            conn.close()
        self.assertEqual(count, 3)


class TestHandleLeadSubmissionSheets(unittest.TestCase):
    """handle_lead_submission delegates to Sheets when available and credentials exist."""

    def _make_fake_creds(self) -> Path:
        tmp = tempfile.NamedTemporaryFile(
            suffix=".json", delete=False, mode="w", encoding="utf-8"
        )
        tmp.write("{}")
        tmp.close()
        return Path(tmp.name)

    def tearDown(self) -> None:
        os.environ.pop("GOOGLE_CREDENTIALS_PATH", None)

    def test_sheets_called_when_available_and_credentials_present(self) -> None:
        creds = self._make_fake_creds()
        os.environ["GOOGLE_CREDENTIALS_PATH"] = str(creds)
        mock_register = MagicMock()
        with (
            patch.object(lc, "_SHEETS_AVAILABLE", True),
            patch.object(lc, "_register_lead", mock_register),
        ):
            result = lc.handle_lead_submission(
                {"name": "Carol", "email": "c@c.com", "company": "SheetsInc"}
            )
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["method"], "sheets")
        mock_register.assert_called_once_with("Carol", "c@c.com", "SheetsInc")
        creds.unlink(missing_ok=True)

    def test_sheets_error_falls_back_to_sqlite(self) -> None:
        creds = self._make_fake_creds()
        os.environ["GOOGLE_CREDENTIALS_PATH"] = str(creds)
        mock_register = MagicMock(side_effect=RuntimeError("quota exceeded"))
        with (
            patch.object(lc, "_SHEETS_AVAILABLE", True),
            patch.object(lc, "_register_lead", mock_register),
        ):
            result = lc.handle_lead_submission({"name": "Dave", "email": "d@d.com"})
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["method"], "sqlite_fallback")
        creds.unlink(missing_ok=True)

    def test_no_credentials_file_uses_sqlite(self) -> None:
        os.environ["GOOGLE_CREDENTIALS_PATH"] = "/nonexistent/path/credentials.json"
        mock_register = MagicMock()
        with (
            patch.object(lc, "_SHEETS_AVAILABLE", True),
            patch.object(lc, "_register_lead", mock_register),
        ):
            result = lc.handle_lead_submission({"name": "Eve", "email": "e@e.com"})
        mock_register.assert_not_called()
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["method"], "sqlite_fallback")


class TestLeadsEndpoint(unittest.TestCase):
    """Integration: POST /api/v1/leads returns capture metadata."""

    def setUp(self) -> None:
        from api.index import app
        self.client = app.test_client()

    def test_post_leads_returns_ok(self) -> None:
        with patch("api.index.handle_lead_submission", return_value={"status": "success", "method": "sqlite_fallback"}):
            resp = self.client.post(
                "/api/v1/leads",
                json={"name": "Frank", "email": "f@f.com", "intent": "reserve"},
            )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("capture", data)
        self.assertEqual(data["capture"]["method"], "sqlite_fallback")


if __name__ == "__main__":
    unittest.main()
