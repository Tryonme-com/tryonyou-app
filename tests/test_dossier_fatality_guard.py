from __future__ import annotations

import unittest
from datetime import datetime

from dossier_fatality_guard import should_activate, summarize_activation


class TestDossierFatalityGuard(unittest.TestCase):
    def test_requires_tuesday_0800(self) -> None:
        monday = datetime(2026, 4, 13, 8, 0, 0)  # Monday
        self.assertFalse(should_activate(monday, "450000", True))

    def test_requires_amount_threshold(self) -> None:
        tuesday = datetime(2026, 4, 14, 8, 0, 0)  # Tuesday
        self.assertFalse(should_activate(tuesday, "449999", True))
        self.assertTrue(should_activate(tuesday, "450000", True))
        self.assertTrue(should_activate(tuesday, "450.000,00", True))

    def test_requires_external_evidence(self) -> None:
        tuesday = datetime(2026, 4, 14, 8, 0, 0)  # Tuesday
        self.assertFalse(should_activate(tuesday, "450000", False))

    def test_summary_message(self) -> None:
        tuesday = datetime(2026, 4, 14, 8, 0, 0)  # Tuesday
        msg_ok = summarize_activation(tuesday, "450000", True)
        self.assertIn("ACTIVADO", msg_ok)
        msg_no = summarize_activation(tuesday, "1000", False)
        self.assertIn("NO ACTIVADO", msg_no)


if __name__ == "__main__":
    unittest.main()
