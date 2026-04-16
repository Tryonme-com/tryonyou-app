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

from commission_audit import run_audit
from core_engine import (
    health_payload,
    mirror_snap_payload,
    model_access_payload,
    perfect_selection_payload,
)


class TestCommissionAudit(unittest.TestCase):
    def test_audit_csv_calculates_confirmed_volume_and_8pct(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            csv_path = Path(td) / "sales.csv"
            csv_path.write_text(
                "fecha_hora,importe_eur,estado,id_transaccion\n"
                "2026-04-13 11:14:31,100.0,CONFIRMADO,T1\n"
                "2026-04-13 11:15:31,50.0,PENDING,T2\n"
                "2026-04-13 11:16:31,200.0,CONFIRMADO,T3\n",
                encoding="utf-8",
            )
            result = run_audit(csv_path)
        self.assertEqual(result["confirmed_transactions"], 2)
        self.assertEqual(result["volumen_total_confirmado_eur"], 300.0)
        self.assertEqual(result["comision_8pct_eur"], 24.0)
        self.assertEqual(result["total_con_comision_eur"], 324.0)


class TestPaymentKillSwitch402(unittest.TestCase):
    def setUp(self) -> None:
        self.prev = os.environ.copy()
        os.environ["JULES_MIRROR_POWER_STATE"] = "on"
        os.environ["PAYMENT_VERIFIED"] = "false"

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self.prev)

    def test_health_exposes_debt_message_and_disables_mirror(self) -> None:
        payload = health_payload()
        self.assertFalse(payload["mirror_enabled"])
        self.assertFalse(payload["payment_verified"])
        self.assertIn("27.500", payload["debt_message"])

    def test_model_access_returns_402_when_payment_not_verified(self) -> None:
        payload, code = model_access_payload({}, {})
        self.assertEqual(code, 402)
        self.assertFalse(payload["payment_verified"])
        self.assertEqual(payload["debt_amount_eur"], 27500.0)
        self.assertIn("Error 402", payload["debt_message"])

    def test_mirror_snap_returns_402_when_payment_not_verified(self) -> None:
        payload, code = mirror_snap_payload({}, {})
        self.assertEqual(code, 402)
        self.assertEqual(payload["error_code"], 402)
        self.assertFalse(payload["payment_verified"])

    def test_perfect_selection_returns_402_when_payment_not_verified(self) -> None:
        payload, code = perfect_selection_payload({}, {})
        self.assertEqual(code, 402)
        self.assertEqual(payload["error_code"], 402)
        self.assertFalse(payload["payment_verified"])


if __name__ == "__main__":
    unittest.main()
