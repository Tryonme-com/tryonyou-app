from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
for _p in (_ROOT, os.path.join(_ROOT, "api")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from logic.falla_commission_manager import GestorFallaV9, JsonFallaMemoryStore


class TestGestorFallaV9(unittest.TestCase):
    def _gestor(self, path: Path) -> GestorFallaV9:
        return GestorFallaV9(memory_store=JsonFallaMemoryStore(path))

    def test_processes_paid_quota_with_commission_and_net(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            gestor = self._gestor(Path(tmp) / "memories.json")

            asiento = gestor.ejecutar_cobro(
                fallero="Pau",
                importe_bruto=100,
                concepto="Cuota Abril",
                transaction_id="tx_100",
            )

            self.assertEqual(asiento["fallero"], "PAU")
            self.assertEqual(asiento["concepto_tipo"], "cuota")
            self.assertEqual(asiento["comision_aplicada_eur"], "8.00 EUR")
            self.assertEqual(asiento["neto_falla_eur"], "92.00 EUR")
            self.assertEqual(asiento["estado"], "PAGADO")
            self.assertEqual(asiento["saldo_pendiente_eur"], "0.00 EUR")

    def test_marks_underpaid_quota_pending_and_updates_balance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            gestor = self._gestor(Path(tmp) / "memories.json")

            asiento = gestor.ejecutar_cobro(
                fallero="Maria",
                importe_bruto=30,
                concepto="Cuota Mayo",
                transaction_id="tx_30",
            )

            self.assertEqual(asiento["estado"], "PENDIENTE_DE_REGULARIZAR")
            self.assertEqual(asiento["saldo_pendiente_eur"], "20.00 EUR")
            self.assertEqual(gestor.resumen()["pendientes_regularizar"], 1)

    def test_duplicate_transaction_is_not_registered_twice(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            gestor = self._gestor(Path(tmp) / "memories.json")
            payload = {
                "fallero": "Vicent",
                "importe_bruto": "50,00 EUR",
                "concepto": "cuota Junio",
                "transaction_id": "tx_dup",
            }

            first = gestor.ejecutar_cobro(payload)
            duplicate = gestor.ejecutar_cobro(payload)

            self.assertFalse(first["duplicado"])
            self.assertTrue(duplicate["duplicado"])
            self.assertEqual(duplicate["status"], "duplicate")
            self.assertEqual(gestor.resumen()["transactions_count"], 1)

    def test_accepts_commission_percent_as_number_8(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            gestor = GestorFallaV9(comision_pct=8, memory_store=JsonFallaMemoryStore(Path(tmp) / "memories.json"))

            asiento = gestor.ejecutar_cobro(
                fallero="Ana",
                importe_bruto=200,
                concepto="Evento cena",
                transaction_id="tx_event",
            )

            self.assertEqual(asiento["comision_pct"], "8.00")
            self.assertEqual(asiento["comision_aplicada_eur"], "16.00 EUR")


if __name__ == "__main__":
    unittest.main()
