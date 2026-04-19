from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import dossier_fatality_guard as guard


class TestDossierFatalityGuard(unittest.TestCase):
    def test_parse_emergency_amount_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / ".emergency_payout"
            p.write_text("TARGET_NODE=0469\nAMOUNT=450000.00\n", encoding="utf-8")
            amount = guard._parse_emergency_amount(p)
            self.assertEqual(amount, 450000.0)

    def test_parse_emergency_amount_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / ".emergency_payout"
            p.write_text("AMOUNT=not_a_number\n", encoding="utf-8")
            amount = guard._parse_emergency_amount(p)
            self.assertIsNone(amount)

    def test_payment_confirmed_from_emergency_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            emergency = root / ".emergency_payout"
            ledger = root / "registro_pagos_hoy.csv"
            emergency.write_text("AMOUNT=450000.00\n", encoding="utf-8")
            ledger.write_text(
                "fecha_hora,importe_eur,estado,id_transaccion\n",
                encoding="utf-8",
            )

            old_emergency = guard.EMERGENCY_PATH
            old_ledger = guard.LEDGER_PATH
            try:
                guard.EMERGENCY_PATH = emergency
                guard.LEDGER_PATH = ledger
                ok, source = guard._payment_confirmed(
                    guard.FatalityConfig(
                        target_amount_eur=450000.0,
                        target_weekday=1,
                        target_hour=8,
                        target_minute=0,
                    )
                )
            finally:
                guard.EMERGENCY_PATH = old_emergency
                guard.LEDGER_PATH = old_ledger

            self.assertTrue(ok)
            self.assertIn(".emergency_payout", source)

    def test_payment_confirmed_from_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            emergency = root / ".emergency_payout"
            ledger = root / "registro_pagos_hoy.csv"
            emergency.write_text("AMOUNT=120.00\n", encoding="utf-8")
            ledger.write_text(
                "fecha_hora,importe_eur,estado,id_transaccion\n"
                "2026-04-19 08:00:00,450000.0,CONFIRMADO,TX-450K\n",
                encoding="utf-8",
            )

            old_emergency = guard.EMERGENCY_PATH
            old_ledger = guard.LEDGER_PATH
            try:
                guard.EMERGENCY_PATH = emergency
                guard.LEDGER_PATH = ledger
                ok, source = guard._payment_confirmed(
                    guard.FatalityConfig(
                        target_amount_eur=450000.0,
                        target_weekday=1,
                        target_hour=8,
                        target_minute=0,
                    )
                )
            finally:
                guard.EMERGENCY_PATH = old_emergency
                guard.LEDGER_PATH = old_ledger

            self.assertTrue(ok)
            self.assertIn("registro_pagos_hoy.csv", source)
            self.assertIn("TX-450K", source)


if __name__ == "__main__":
    unittest.main()
