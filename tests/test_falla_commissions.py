from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_API = os.path.join(_ROOT, "api")
for _p in (_ROOT, _API):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from falla_commissions import get_falla_memory, process_falla_batch, process_falla_payment


class TestFallaCommissions(unittest.TestCase):
    def setUp(self) -> None:
        self.prev_env = os.environ.copy()
        self.tmpdir = tempfile.TemporaryDirectory()
        self.memory_path = Path(self.tmpdir.name) / "falla_memories.jsonl"
        os.environ["FALLA_MEMORIES_PATH"] = str(self.memory_path)
        os.environ["FALLA_COMMISSION_PCT"] = "0.08"
        os.environ["FALLA_CUOTA_BASE_EUR"] = "50"

    def tearDown(self) -> None:
        self.tmpdir.cleanup()
        os.environ.clear()
        os.environ.update(self.prev_env)

    def test_process_payment_calculates_8pct_and_net(self) -> None:
        result = process_falla_payment(
            {
                "transaction_id": "pay_001",
                "fallero_id": "F-7",
                "nombre": "Pau",
                "importe_bruto": 100,
                "concepto": "Cuota Abril",
                "fecha": "2026-05-03",
                "source": "webhook",
            }
        )

        asiento = result["asiento"]
        self.assertEqual(result["status"], "ok")
        self.assertEqual(asiento["fallero"], "PAU")
        self.assertEqual(asiento["fallero_id"], "F-7")
        self.assertEqual(asiento["importe_bruto_eur"], 100.0)
        self.assertEqual(asiento["comision_eur"], 8.0)
        self.assertEqual(asiento["neto_falla_eur"], 92.0)
        self.assertEqual(asiento["estado"], "PAGADO")
        self.assertTrue(asiento["concepto_valido"])

    def test_low_payment_is_marked_pending_to_regularize(self) -> None:
        result = process_falla_payment(
            {
                "transaction_id": "pay_low",
                "fallero": "Marta",
                "amount_eur": "30,00 EUR",
                "concepto": "evento infantil",
            }
        )

        asiento = result["asiento"]
        self.assertEqual(asiento["estado"], "PENDIENTE_DE_REGULARIZAR")
        self.assertEqual(asiento["saldo_pendiente_eur"], 20.0)
        self.assertEqual(asiento["comision_eur"], 2.4)

    def test_duplicate_transaction_is_not_appended_twice(self) -> None:
        payload = {
            "transaction_id": "pay_dup",
            "fallero": "Pau",
            "bruto": 50,
            "concepto": "loteria navidad",
        }

        first = process_falla_payment(payload)
        second = process_falla_payment(payload)
        memory = get_falla_memory()

        self.assertEqual(first["status"], "ok")
        self.assertEqual(second["status"], "duplicate")
        self.assertEqual(memory["entries_count"], 1)
        self.assertEqual(memory["totals"]["importe_bruto_eur"], 50.0)

    def test_batch_reports_partial_errors_without_losing_valid_records(self) -> None:
        result = process_falla_batch(
            {
                "records": [
                    {
                        "transaction_id": "ok_1",
                        "fallero": "Ana",
                        "importe_eur": 75,
                        "concepto": "cuota mayo",
                    },
                    {
                        "transaction_id": "bad_1",
                        "fallero": "",
                        "importe_eur": 75,
                        "concepto": "cuota mayo",
                    },
                ]
            }
        )

        self.assertEqual(result["status"], "partial_error")
        self.assertEqual(result["processed_count"], 1)
        self.assertEqual(result["errors_count"], 1)
        self.assertEqual(result["errors"][0]["error"], "fallero_required")


if __name__ == "__main__":
    unittest.main()
