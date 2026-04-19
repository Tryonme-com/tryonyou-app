"""Tests del Batch Payout Engine SacMuseum/Lafayette."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from scripts import sacmuseum_h2_stripe as engine


class _FakeStripe:
    def __init__(
        self,
        *,
        balances: list[dict[str, object]],
        transactions: list[dict[str, object]],
        payout_id: str = "po_fake_123",
    ) -> None:
        self._balances = list(balances)
        self._transactions = list(transactions)
        self._payout_id = payout_id
        self.payout_calls: list[dict[str, object]] = []

        self.Balance = SimpleNamespace(retrieve=self._balance_retrieve)
        self.BalanceTransaction = SimpleNamespace(list=self._balance_transaction_list)
        self.Payout = SimpleNamespace(create=self._payout_create)
        self.Charge = SimpleNamespace(retrieve=self._charge_retrieve)

    def _balance_retrieve(self, stripe_account: str | None = None) -> dict[str, object]:
        _ = stripe_account
        if self._balances:
            return self._balances.pop(0)
        return {"available": [], "pending": []}

    def _balance_transaction_list(
        self, stripe_account: str | None = None, limit: int = 100
    ) -> list[dict[str, object]]:
        _ = stripe_account
        return list(self._transactions)[:limit]

    def _payout_create(self, **kwargs: object) -> SimpleNamespace:
        self.payout_calls.append(kwargs)
        return SimpleNamespace(id=self._payout_id)

    def _charge_retrieve(
        self, charge_id: str, stripe_account: str | None = None
    ) -> dict[str, object]:
        _ = stripe_account
        return {"id": charge_id, "payment_intent": "pi_3OzL_from_charge"}


class TestSacmuseumBatchPayout(unittest.TestCase):
    def test_batch_crea_payout_y_registra_po_en_log_soberania(self) -> None:
        fake = _FakeStripe(
            balances=[{"available": [{"amount": 1500, "currency": "eur"}], "pending": []}],
            transactions=[
                {
                    "id": "txn_match_1",
                    "status": "available",
                    "payment_intent": "pi_3OzL9000",
                    "net": 1500,
                    "currency": "eur",
                    "available_on": 1710000000,
                }
            ],
            payout_id="po_123456",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "sovereignty_payout_log.jsonl"
            state_path = Path(tmpdir) / "lafayette_batch_payout_state.json"
            summary = engine.run_lafayette_batch_payout(
                fake,
                "acct_123",
                log_path=log_path,
                state_path=state_path,
                dry_run=False,
            )

            self.assertEqual(len(fake.payout_calls), 1)
            self.assertEqual(summary["detected_candidates"], 1)
            created = summary["created"]
            self.assertIsInstance(created, list)
            self.assertEqual(len(created), 1)
            self.assertEqual(created[0]["payout_id"], "po_123456")

            log_lines = log_path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(log_lines), 1)
            payload = json.loads(log_lines[0])
            self.assertEqual(payload["payout_id"], "po_123456")
            self.assertEqual(payload["payment_intent_id"], "pi_3OzL9000")

            state_payload = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertIn("txn_match_1", state_payload["processed_balance_transactions"])

    def test_batch_omite_txn_ya_procesada(self) -> None:
        fake = _FakeStripe(
            balances=[{"available": [{"amount": 2000, "currency": "eur"}], "pending": []}],
            transactions=[
                {
                    "id": "txn_repeat",
                    "status": "available",
                    "payment_intent": "pi_3OzL_repeat",
                    "net": 1000,
                    "currency": "eur",
                    "available_on": 1710000100,
                }
            ],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "lafayette_batch_payout_state.json"
            state_path.write_text(
                json.dumps({"processed_balance_transactions": ["txn_repeat"]}),
                encoding="utf-8",
            )
            summary = engine.run_lafayette_batch_payout(
                fake,
                "acct_123",
                log_path=Path(tmpdir) / "sovereignty_payout_log.jsonl",
                state_path=state_path,
                dry_run=False,
            )

            self.assertEqual(len(fake.payout_calls), 0)
            self.assertEqual(summary["skipped_processed"], 1)

    def test_watch_dispara_batch_en_cada_cambio_de_balance(self) -> None:
        fake = _FakeStripe(
            balances=[
                {"available": [{"amount": 1000, "currency": "eur"}], "pending": []},
                {"available": [{"amount": 2000, "currency": "eur"}], "pending": []},
            ],
            transactions=[],
        )

        with patch(
            "scripts.sacmuseum_h2_stripe.run_lafayette_batch_payout",
            return_value={
                "mode": "lafayette_batch",
                "created": [],
                "detected_candidates": 0,
                "errors": [],
                "skipped_processed": 0,
                "skipped_insufficient_balance": 0,
            },
        ) as mock_batch:
            rc = engine.run_lafayette_watch_loop(
                fake,
                "acct_123",
                pi_prefix="pi_3OzL",
                currency="eur",
                statement_descriptor="LAFAYETTE AUTO",
                poll_interval_sec=0.01,
                scan_limit=100,
                max_polls=2,
            )

        self.assertEqual(rc, 0)
        self.assertEqual(mock_batch.call_count, 2)


if __name__ == "__main__":
    unittest.main()
