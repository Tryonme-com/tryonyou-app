from __future__ import annotations

import json
import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from orquestador_autonomia_total import (
    DEFAULT_DEPLOY_CHAT_ID,
    activate_fatality_dossier,
    has_capital_entry,
    is_tuesday_0800,
    telegram_credentials,
)


class TestOrquestadorAutonomiaTotal(unittest.TestCase):
    def setUp(self) -> None:
        self._old_env = {
            "TRYONYOU_DEPLOY_BOT_TOKEN": os.environ.get("TRYONYOU_DEPLOY_BOT_TOKEN"),
            "TELEGRAM_BOT_TOKEN": os.environ.get("TELEGRAM_BOT_TOKEN"),
            "TELEGRAM_TOKEN": os.environ.get("TELEGRAM_TOKEN"),
            "TRYONYOU_DEPLOY_CHAT_ID": os.environ.get("TRYONYOU_DEPLOY_CHAT_ID"),
            "TELEGRAM_CHAT_ID": os.environ.get("TELEGRAM_CHAT_ID"),
        }
        for key in self._old_env:
            os.environ.pop(key, None)

    def tearDown(self) -> None:
        for key, value in self._old_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_is_tuesday_0800_true_inside_tolerance(self) -> None:
        dt = datetime(2026, 4, 14, 8, 5, tzinfo=ZoneInfo("Europe/Paris"))  # Tuesday
        self.assertTrue(is_tuesday_0800(dt))

    def test_is_tuesday_0800_false_wrong_day(self) -> None:
        dt = datetime(2026, 4, 15, 8, 0, tzinfo=ZoneInfo("Europe/Paris"))  # Wednesday
        self.assertFalse(is_tuesday_0800(dt))

    def test_has_capital_entry_true_when_target_reached(self) -> None:
        treasury = {"capital_eur": 450_000.0}
        self.assertTrue(has_capital_entry(treasury, 450_000.0))

    def test_has_capital_entry_false_when_below_target(self) -> None:
        treasury = {"capital_eur": 449_999.99}
        self.assertFalse(has_capital_entry(treasury, 450_000.0))

    def test_telegram_credentials_fallback_chat_id(self) -> None:
        os.environ["TELEGRAM_BOT_TOKEN"] = "token-demo"
        token, chat_id = telegram_credentials()
        self.assertEqual(token, "token-demo")
        self.assertEqual(chat_id, DEFAULT_DEPLOY_CHAT_ID)

    def test_activate_fatality_dossier_writes_expected_payload(self) -> None:
        treasury = {
            "capital_eur": 450_000.0,
            "capital_label": "Capital Social Blindado",
            "reserve_eur": 449_600.0,
        }
        now = datetime(2026, 4, 14, 8, 0, tzinfo=ZoneInfo("Europe/Paris"))

        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            os.environ["VIP_FLOW_RATE"] = "98.5"
            dossier_path = activate_fatality_dossier(
                treasury_status=treasury,
                now=now,
                expected_eur=450_000.0,
                output_dir=out_dir,
            )
            self.assertTrue(dossier_path.exists())

            payload = json.loads(dossier_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "ACTIVE")
            self.assertEqual(payload["capital_target_eur"], 450_000.0)
            self.assertEqual(payload["capital_reported_eur"], 450_000.0)
            self.assertTrue(payload["vip_flow_alert"])

        os.environ.pop("VIP_FLOW_RATE", None)


if __name__ == "__main__":
    unittest.main()
