from __future__ import annotations

import json
import os
import tempfile
import unittest
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

import martes_0800_dossier_fatality as mod


class StubNotifier:
    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled
        self.messages: list[str] = []

    def send(self, text: str) -> bool:
        self.messages.append(text)
        return True


class TestTuesdayFatality(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmpdir.name)
        self.dossier = self.root / "dossier_fatality.json"
        self.status = self.root / "logs" / "dossier_fatality_activation.json"
        self.dossier.write_text(
            json.dumps(
                {
                    "estrategia": "DOSSIER FATALITY V10",
                    "sello_legal": "Patente PCT/EP2025/067317 | SIRET 94361019600017",
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_rejects_closed_window_without_force(self) -> None:
        now = datetime(2026, 4, 13, 8, 0)  # Monday
        rc = mod.activate_dossier_fatality(
            force=False,
            tz_name="Europe/Paris",
            confirmed_eur=Decimal("450000"),
            notifier=StubNotifier(),
            now_local=now,
            dossier_path=self.dossier,
            status_path=self.status,
        )
        self.assertEqual(rc, 2)
        self.assertFalse(self.status.exists())

    def test_activates_when_tuesday_8am_and_amount_ok(self) -> None:
        now = datetime(2026, 4, 14, 8, 0)  # Tuesday
        notifier = StubNotifier()
        rc = mod.activate_dossier_fatality(
            force=False,
            tz_name="Europe/Paris",
            confirmed_eur=Decimal("450000"),
            notifier=notifier,
            now_local=now,
            dossier_path=self.dossier,
            status_path=self.status,
        )
        self.assertEqual(rc, 0)
        self.assertTrue(self.status.exists())
        data = json.loads(self.status.read_text(encoding="utf-8"))
        self.assertEqual(data["status"], "DOSSIER_FATALITY_ACTIVATED")
        self.assertEqual(data["capital_confirmed_eur"], "450000.00")
        self.assertEqual(data["bot_handle"], "@tryonyou_deploy_bot")
        self.assertGreaterEqual(len(notifier.messages), 2)

    def test_fails_when_amount_insufficient(self) -> None:
        now = datetime(2026, 4, 14, 8, 0)
        rc = mod.activate_dossier_fatality(
            force=False,
            tz_name="Europe/Paris",
            confirmed_eur=Decimal("449999"),
            notifier=StubNotifier(),
            now_local=now,
            dossier_path=self.dossier,
            status_path=self.status,
        )
        self.assertEqual(rc, 3)
        self.assertFalse(self.status.exists())

    def test_reads_confirmed_amount_from_environment(self) -> None:
        now = datetime(2026, 4, 14, 8, 0)
        with patch.dict(os.environ, {"TRYONYOU_CONFIRMED_CAPITAL_EUR": "450000"}, clear=False):
            rc = mod.activate_dossier_fatality(
                force=False,
                tz_name="Europe/Paris",
                confirmed_eur=None,
                notifier=StubNotifier(),
                now_local=now,
                dossier_path=self.dossier,
                status_path=self.status,
            )
        self.assertEqual(rc, 0)

    def test_vip_flow_rate_alert_below_99(self) -> None:
        now = datetime(2026, 4, 14, 8, 0)
        with patch.dict(os.environ, {"VIP_FLOW_RATE": "98.7"}, clear=False):
            rc = mod.activate_dossier_fatality(
                force=True,
                tz_name="Europe/Paris",
                confirmed_eur=Decimal("450000"),
                notifier=StubNotifier(),
                now_local=now,
                dossier_path=self.dossier,
                status_path=self.status,
            )
        self.assertEqual(rc, 0)
        data = json.loads(self.status.read_text(encoding="utf-8"))
        self.assertTrue(data["efecto_paloma"]["vip_flow_alert"])


if __name__ == "__main__":
    unittest.main()
