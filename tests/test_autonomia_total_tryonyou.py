"""Tests de autonomia_total_tryonyou.py."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock

import autonomia_total_tryonyou as auto


class TestAutonomiaTotalTryOnYou(unittest.TestCase):
    def test_in_security_window_true_for_tuesday_0800(self) -> None:
        dt = datetime(2026, 4, 14, 8, 5)  # Tuesday
        self.assertTrue(auto.in_security_window(now=dt, tolerance_minutes=10))

    def test_in_security_window_false_for_other_day(self) -> None:
        dt = datetime(2026, 4, 13, 8, 5)  # Monday
        self.assertFalse(auto.in_security_window(now=dt, tolerance_minutes=10))

    def test_detect_funds_confirmation_env_flag(self) -> None:
        with mock.patch.dict(
            os.environ,
            {"TRYONYOU_FUNDS_450K_CONFIRMED": "1", "TRYONYOU_FUNDS_450K_REFERENCE": "bank_ref"},
            clear=False,
        ):
            ok, source = auto.detect_funds_confirmation()
        self.assertTrue(ok)
        self.assertIn("confirmed_by_env", source)

    def test_sanitize_token_removes_spaces(self) -> None:
        raw = "8788913760:AAE2 gS0M8v1_S96H9F m8I-K1U9Z_6-R-K48\n"
        clean = auto._sanitize_token(raw)
        self.assertNotIn(" ", clean)
        self.assertNotIn("\n", clean)
        self.assertIn("8788913760:AAE2", clean)

    def test_activate_dossier_fatality_pending_without_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dossier = Path(tmp) / "dossier_fatality.json"
            dossier.write_text("{}", encoding="utf-8")
            with mock.patch.object(auto, "DOSSIER", dossier):
                out = auto.activate_dossier_fatality(
                    force=False,
                    now=datetime(2026, 4, 14, 8, 2),  # Tuesday 08:02
                    tolerance_minutes=10,
                )
            self.assertEqual(out["status"], "pending_confirmation")
            data = json.loads(dossier.read_text(encoding="utf-8"))
            self.assertIn("capital_protection", data)

    def test_activate_dossier_fatality_active_with_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dossier = Path(tmp) / "dossier_fatality.json"
            dossier.write_text("{}", encoding="utf-8")
            env = {"TRYONYOU_FUNDS_450K_CONFIRMED": "1"}
            with mock.patch.dict(os.environ, env, clear=False):
                with mock.patch.object(auto, "DOSSIER", dossier):
                    out = auto.activate_dossier_fatality(
                        force=False,
                        now=datetime(2026, 4, 14, 8, 2),
                        tolerance_minutes=10,
                    )
            self.assertEqual(out["status"], "active")

    def test_write_memory_notes_creates_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "bunker_sovereignty.ma"
            auto.write_memory_notes(p)
            text = p.read_text(encoding="utf-8")
            self.assertIn("@tryonyou_deploy_bot", text)
            self.assertIn("Oberkampf 75011", text)
            self.assertIn("450000 EUR", text)


if __name__ == "__main__":
    unittest.main()
