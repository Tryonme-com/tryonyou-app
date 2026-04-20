"""Tests for batch_payout_engine.py."""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
import types
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from batch_payout_engine import BatchPayoutConfig, run_cycle


class _FakePaymentIntent:
    records: dict[str, dict[str, object]] = {}

    @classmethod
    def retrieve(cls, intent_id: str):
        return cls.records[intent_id]


class _FakeBalance:
    available_amount = 0
    currency = "eur"

    @classmethod
    def retrieve(cls):
        return {
            "available": [
                {
                    "amount": cls.available_amount,
                    "currency": cls.currency,
                }
            ]
        }


class _FakePayout:
    created_params: list[dict[str, object]] = []

    @classmethod
    def create(cls, **kwargs):
        cls.created_params.append(dict(kwargs))
        return {"id": "po_batch_001"}


def _build_fake_stripe() -> types.SimpleNamespace:
    _FakePayout.created_params = []
    return types.SimpleNamespace(
        api_key="",
        PaymentIntent=_FakePaymentIntent,
        Balance=_FakeBalance,
        Payout=_FakePayout,
    )


class TestBatchPayoutEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp(prefix="batch_payout_engine_")
        self.tmp_path = Path(self.tmp)
        self.compliance_log = self.tmp_path / "compliance_logs.jsonl"
        self.state_file = self.tmp_path / "state.json"
        os.environ["SUPABASE_INFRA_STATUS"] = "SUPABASE ARMORED"
        os.environ["SOUVERAINETE_STATUS"] = "SOUVERAINETÉ:1"

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)
        os.environ.pop("SUPABASE_INFRA_STATUS", None)
        os.environ.pop("SOUVERAINETE_STATUS", None)
        if "stripe" in sys.modules:
            sys.modules.pop("stripe", None)

    def _config(self, *, confirm_payout: bool = True) -> BatchPayoutConfig:
        return BatchPayoutConfig(
            payment_intent_ids=(
                "pi_3OzL9k_001",
                "pi_3OzL9k_002",
                "pi_3OzL9k_003",
                "pi_3OzL9k_004",
                "pi_3OzL9k_005",
            ),
            payment_intent_prefix="pi_3OzL9k",
            target_count=5,
            max_intent_scan=20,
            poll_seconds=5,
            timezone_name="Europe/Paris",
            bank_open_hour=9,
            bank_open_minute=0,
            bank_open_weekdays=(0, 1, 2, 3, 4),
            compliance_log_paths=(self.compliance_log,),
            compliance_markers=("anomaly", "blocked", "fraud"),
            compliance_strict=True,
            notify_webhook_url="",
            confirm_payout=confirm_payout,
            state_file=self.state_file,
            payout_currency="eur",
            payout_amount_cents_override=None,
            payout_descriptor="OMEGA10 BATCH",
            payout_destination_account="",
            expected_infra_state="SUPABASE ARMORED",
            expected_souverainete_state="SOUVERAINETE:1",
        )

    def test_blocks_when_compliance_has_anomaly(self) -> None:
        self.compliance_log.write_text(
            '{"level":"critical","message":"anomaly detected in compliance_logs"}\n',
            encoding="utf-8",
        )
        result = run_cycle(
            self._config(),
            now=datetime(2026, 4, 20, 10, 0, tzinfo=ZoneInfo("Europe/Paris")),
        )
        self.assertEqual(result["status"], "blocked_compliance")
        compliance = result["compliance"]
        self.assertTrue(compliance["blocked"])
        self.assertEqual(compliance["reason"], "anomaly_detected")
        self.assertEqual(len(compliance["anomalies"]), 1)

    def test_executes_payout_once_and_then_reports_already_executed(self) -> None:
        self.compliance_log.write_text('{"level":"info","message":"all clear"}\n', encoding="utf-8")
        for idx in range(1, 6):
            _FakePaymentIntent.records[f"pi_3OzL9k_00{idx}"] = {
                "id": f"pi_3OzL9k_00{idx}",
                "status": "succeeded",
                "currency": "eur",
                "amount_received": 10_000,
                "created": 1700000000 + idx,
            }
        _FakeBalance.available_amount = 80_000
        fake_stripe = _build_fake_stripe()
        sys.modules["stripe"] = fake_stripe

        with (
            patch("batch_payout_engine.resolve_stripe_secret", return_value="sk_live_test"),
            patch("batch_payout_engine._register_internal_payout") as register_payout,
        ):
            first = run_cycle(
                self._config(confirm_payout=True),
                now=datetime(2026, 4, 21, 10, 5, tzinfo=ZoneInfo("Europe/Paris")),
            )
            second = run_cycle(
                self._config(confirm_payout=True),
                now=datetime(2026, 4, 21, 10, 6, tzinfo=ZoneInfo("Europe/Paris")),
            )

        self.assertEqual(first["status"], "executed")
        self.assertEqual(first["execution"]["payout_id"], "po_batch_001")
        self.assertEqual(second["status"], "already_executed")
        self.assertEqual(len(_FakePayout.created_params), 1)
        self.assertEqual(_FakePayout.created_params[0]["amount"], 50_000)
        self.assertEqual(_FakePayout.created_params[0]["currency"], "eur")
        register_payout.assert_called_once()


if __name__ == "__main__":
    unittest.main()
