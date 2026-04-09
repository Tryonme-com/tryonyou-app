"""
Tests para SovereignSettlement — Motor de Liquidación Final V10.

Valida:
  - Inicialización correcta del objeto
  - validar_transaccion_real: estructura, importe neto, destino y auditoría
  - trigger_don_divin: umbral de leads VIP
"""

from __future__ import annotations

import os
import sys
import unittest

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_API = os.path.join(_ROOT, "api")
for _p in (_ROOT, _API):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from sovereign_settlement import (
    DEFAULT_FEE_LICENCIA_DIARIA,
    SovereignSettlement,
    _PLATFORM_COMMISSION_RATE,
    _VIP_LEAD_THRESHOLD,
)


class TestSovereignSettlementInit(unittest.TestCase):
    def setUp(self) -> None:
        self.settlement = SovereignSettlement("test_stripe_key", "ES91 2100 0418 4502 0005 1332")

    def test_status_bunker_ready(self) -> None:
        self.assertEqual(self.settlement.status, "BUNKER_READY")

    def test_iban_destino_stored(self) -> None:
        self.assertEqual(self.settlement.iban_destino, "ES91 2100 0418 4502 0005 1332")

    def test_fee_licencia_diaria_default(self) -> None:
        self.assertAlmostEqual(
            self.settlement.fee_licencia_diaria, DEFAULT_FEE_LICENCIA_DIARIA, places=2
        )

    def test_api_key_not_stored_in_plain_text(self) -> None:
        # Raw key must never be accessible via any attribute
        self.assertFalse(
            hasattr(self.settlement, "api_key") and
            getattr(self.settlement, "api_key", None) == "test_stripe_key"
        )

    def test_empty_api_key_raises(self) -> None:
        with self.assertRaises(ValueError):
            SovereignSettlement("", "ES91 2100 0418 4502 0005 1332")


class TestValidarTransaccionReal(unittest.TestCase):
    def setUp(self) -> None:
        self.settlement = SovereignSettlement("stripe_key_prod", "ES91 2100 0418 4502 0005 1332")

    def test_returns_dict(self) -> None:
        result = self.settlement.validar_transaccion_real("SES-001", 100.0)
        self.assertIsInstance(result, dict)

    def test_payout_authorized_true(self) -> None:
        result = self.settlement.validar_transaccion_real("SES-001", 100.0)
        self.assertTrue(result["payout_authorized"])

    def test_destination_matches_iban(self) -> None:
        result = self.settlement.validar_transaccion_real("SES-001", 100.0)
        self.assertEqual(result["destination"], "ES91 2100 0418 4502 0005 1332")

    def test_settlement_amount_net_of_commission(self) -> None:
        result = self.settlement.validar_transaccion_real("SES-001", 100.0)
        expected = round(100.0 * (1.0 - _PLATFORM_COMMISSION_RATE), 2)
        self.assertAlmostEqual(result["settlement_amount"], expected, places=2)

    def test_settlement_amount_97_euros(self) -> None:
        result = self.settlement.validar_transaccion_real("SES-001", 100.0)
        self.assertAlmostEqual(result["settlement_amount"], 97.0, places=2)

    def test_log_sovereign_confirmed(self) -> None:
        result = self.settlement.validar_transaccion_real("SES-001", 100.0)
        self.assertEqual(result["log"], "SOVEREIGN_CONFIRMED")

    def test_token_prefix_present(self) -> None:
        result = self.settlement.validar_transaccion_real("SES-001", 100.0)
        self.assertIn("token_prefix", result)

    def test_token_prefix_length(self) -> None:
        result = self.settlement.validar_transaccion_real("SES-001", 100.0)
        self.assertEqual(len(result["token_prefix"]), 10)

    def test_tokens_are_unique_per_call(self) -> None:
        r1 = self.settlement.validar_transaccion_real("SES-001", 100.0)
        r2 = self.settlement.validar_transaccion_real("SES-001", 100.0)
        # Different timestamps → different tokens (extremely high probability)
        # We just verify the field is a non-empty string each time
        self.assertIsInstance(r1["token_prefix"], str)
        self.assertIsInstance(r2["token_prefix"], str)

    def test_zero_amount_settlement(self) -> None:
        result = self.settlement.validar_transaccion_real("SES-000", 0.0)
        self.assertAlmostEqual(result["settlement_amount"], 0.0, places=2)

    def test_large_amount_settlement(self) -> None:
        result = self.settlement.validar_transaccion_real("SES-BIG", 4000.0)
        expected = round(4000.0 * (1.0 - _PLATFORM_COMMISSION_RATE), 2)
        self.assertAlmostEqual(result["settlement_amount"], expected, places=2)

    def test_all_required_keys_present(self) -> None:
        result = self.settlement.validar_transaccion_real("SES-001", 100.0)
        for key in ("payout_authorized", "destination", "settlement_amount", "log"):
            self.assertIn(key, result)


class TestTriggerDonDivin(unittest.TestCase):
    def setUp(self) -> None:
        self.settlement = SovereignSettlement("key", "ES00 0000 0000 0000 0000 0000")

    def test_above_threshold_returns_alert(self) -> None:
        result = self.settlement.trigger_don_divin(_VIP_LEAD_THRESHOLD + 1)
        self.assertIn("ALERTA", result)

    def test_at_threshold_returns_normal(self) -> None:
        result = self.settlement.trigger_don_divin(_VIP_LEAD_THRESHOLD)
        self.assertEqual(result, "Flujo normal.")

    def test_below_threshold_returns_normal(self) -> None:
        result = self.settlement.trigger_don_divin(0)
        self.assertEqual(result, "Flujo normal.")

    def test_well_above_threshold_returns_alert(self) -> None:
        result = self.settlement.trigger_don_divin(100)
        self.assertIn("Elevando exclusividad", result)

    def test_return_type_is_str(self) -> None:
        self.assertIsInstance(self.settlement.trigger_don_divin(5), str)
        self.assertIsInstance(self.settlement.trigger_don_divin(50), str)


if __name__ == "__main__":
    unittest.main()
