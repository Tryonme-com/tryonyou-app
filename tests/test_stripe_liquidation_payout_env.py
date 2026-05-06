"""Tests for guarded Stripe liquidation payout."""

from __future__ import annotations

import os
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import stripe_liquidation_payout_env as module


class _FakeBalance:
    @classmethod
    def retrieve(cls):
        return {"available": [{"amount": 250_000, "currency": "eur"}]}


class _FakePayout:
    created_params: list[dict[str, object]] = []

    @classmethod
    def create(cls, **kwargs):
        cls.created_params.append(dict(kwargs))
        return types.SimpleNamespace(id="po_guarded_001")


class TestStripeLiquidationPayoutEnv(unittest.TestCase):
    def setUp(self) -> None:
        self.old_env = {
            key: os.environ.pop(key, None)
            for key in (
                "STRIPE_PAYOUT_CONFIRM",
                "STRIPE_PAYOUT_EXECUTION_REF",
                "STRIPE_PAYOUT_RESERVE_CENTS",
                "STRIPE_PAYOUT_MAX_CENTS",
                "STRIPE_PAYOUT_CURRENCY",
                "STRIPE_PAYOUT_IDEMPOTENCY_KEY",
            )
        }
        _FakePayout.created_params = []
        sys.modules["stripe"] = types.SimpleNamespace(
            api_key="",
            Balance=_FakeBalance,
            Payout=_FakePayout,
        )

    def tearDown(self) -> None:
        for key, value in self.old_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        sys.modules.pop("stripe", None)

    def test_rejects_test_key_for_live_liquidation(self) -> None:
        with patch.object(module, "resolve_stripe_secret", return_value="sk_test_123"):
            self.assertEqual(module.liquidacion_inmediata(dry_run=True), 2)

    def test_dry_run_does_not_create_payout(self) -> None:
        with patch.object(module, "resolve_stripe_secret", return_value="sk_live_123"):
            self.assertEqual(module.liquidacion_inmediata(dry_run=True), 0)
        self.assertEqual(_FakePayout.created_params, [])

    def test_confirm_requires_execution_reference(self) -> None:
        os.environ["STRIPE_PAYOUT_CONFIRM"] = "1"
        with patch.object(module, "resolve_stripe_secret", return_value="sk_live_123"):
            self.assertEqual(module.liquidacion_inmediata(dry_run=False), 4)
        self.assertEqual(_FakePayout.created_params, [])

    def test_confirm_uses_reserve_limit_metadata_and_idempotency(self) -> None:
        os.environ["STRIPE_PAYOUT_CONFIRM"] = "1"
        os.environ["STRIPE_PAYOUT_EXECUTION_REF"] = "qonto-ref-450k"
        os.environ["STRIPE_PAYOUT_RESERVE_CENTS"] = "50_000"
        os.environ["STRIPE_PAYOUT_MAX_CENTS"] = "125000"
        with patch.object(module, "resolve_stripe_secret", return_value="sk_live_123"):
            self.assertEqual(module.liquidacion_inmediata(dry_run=False), 0)

        self.assertEqual(len(_FakePayout.created_params), 1)
        params = _FakePayout.created_params[0]
        self.assertEqual(params["amount"], 125_000)
        self.assertEqual(params["currency"], "eur")
        self.assertIn("idempotency_key", params)
        metadata = params["metadata"]
        self.assertEqual(metadata["execution_ref"], "qonto-ref-450k")
        self.assertEqual(metadata["available_cents"], "250000")
        self.assertEqual(metadata["reserve_cents"], "125000")


if __name__ == "__main__":
    unittest.main()
