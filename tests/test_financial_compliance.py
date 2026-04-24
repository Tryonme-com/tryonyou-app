"""Tests reconciliation F-2026-001 (capital ≥ factura → OK)."""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_API = os.path.join(_ROOT, "api")
for _p in (_ROOT, _API):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import financial_compliance as fc


class TestCapitalCoversInvoice(unittest.TestCase):
    def test_capital_gte_invoice_is_matched_ok(self) -> None:
        ledger = {
            "nivel_1_tesoreria_operativa": {"total_eur": 527_588.00},
            "nivel_2_contrato_marco": {"total_ttc_eur": 1_160_767.21},
        }
        inv = {"importe_ttc_eur": 1_160_767.21, "statut": "EMISE"}
        with patch.object(fc, "master_ledger", return_value=ledger), patch.object(fc, "FACTURA_F_2026_001", inv):
            rep = fc.build_financial_reconciliation_report()
        self.assertEqual(rep.get("reconciliation_status"), "OK")
        rec = rep.get("reconciliation") or {}
        self.assertEqual(rec.get("status"), "MATCHED")
        self.assertEqual(rec.get("reconciliation_status"), "OK")
        self.assertFalse(rec.get("payout_blocked"))
        self.assertTrue(rec.get("payout_trigger"))
        self.assertGreater(float(rec.get("treasury_reserve_eur") or 0), 0.0)

    def test_invoice_exceeds_contract_discrepancy(self) -> None:
        ledger = {
            "nivel_1_tesoreria_operativa": {"total_eur": 10_000.00},
            "nivel_2_contrato_marco": {"total_ttc_eur": 100_000.00},
        }
        inv = {"importe_ttc_eur": 1_160_767.21, "statut": "EMISE"}
        with patch.object(fc, "master_ledger", return_value=ledger), patch.object(fc, "FACTURA_F_2026_001", inv):
            rep = fc.build_financial_reconciliation_report()
        self.assertEqual(rep.get("reconciliation_status"), "DISCREPANCY")
        rec = rep.get("reconciliation") or {}
        self.assertEqual(rec.get("status"), "DISCREPANCY_DETECTED")
        self.assertTrue(rec.get("payout_blocked"))


if __name__ == "__main__":
    unittest.main()
