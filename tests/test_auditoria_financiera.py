"""Tests for auditoria_financiera — secure financial audit using env vars."""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from auditoria_financiera import obtener_auditoria_financiera, PAYOUT_LIMIT


class TestObtenerAuditoriaFinancieraSinClave(unittest.TestCase):
    """Auditoría sin clave configurada devuelve error."""

    def test_missing_key_returns_error(self) -> None:
        with patch.dict(
            os.environ,
            {"STRIPE_SECRET_KEY_FR": "", "STRIPE_SECRET_KEY_NUEVA": "", "STRIPE_SECRET_KEY": ""},
            clear=False,
        ):
            result = obtener_auditoria_financiera()
        self.assertFalse(result["ok"])
        self.assertIsNone(result["saldo_disponible"])
        self.assertEqual(result["payouts"], [])
        self.assertIn("STRIPE_SECRET_KEY", result["error"])


class TestObtenerAuditoriaFinancieraConClave(unittest.TestCase):
    """Auditoría exitosa con clave de entorno y mocks de Stripe."""

    def setUp(self) -> None:
        os.environ["STRIPE_SECRET_KEY_FR"] = "sk_test_dummy"

    def _make_balance(self, amount_cents: int = 12_345_00, currency: str = "eur") -> MagicMock:
        entry = {"amount": amount_cents, "currency": currency}
        bal = MagicMock()
        bal.available = [entry]
        return bal

    def _make_payout(self, pid: str, amount: int, status: str) -> MagicMock:
        p = MagicMock()
        p.id = pid
        p.amount = amount
        p.status = status
        return p

    def test_success_returns_ok(self) -> None:
        bal = self._make_balance(50_000_00)
        p1 = self._make_payout("po_1", 27_500_00, "paid")
        p2 = self._make_payout("po_2", 22_500_00, "pending")
        payout_list = MagicMock()
        payout_list.data = [p1, p2]

        with patch("stripe.Balance.retrieve", return_value=bal), \
             patch("stripe.Payout.list", return_value=payout_list):
            result = obtener_auditoria_financiera()

        self.assertTrue(result["ok"])
        self.assertAlmostEqual(result["saldo_disponible"], 50_000.00, places=2)
        self.assertEqual(len(result["payouts"]), 2)
        self.assertEqual(result["payouts"][0]["id"], "po_1")
        self.assertAlmostEqual(result["payouts"][0]["amount_eur"], 27_500.00, places=2)
        self.assertEqual(result["payouts"][0]["status"], "paid")

    def test_payout_list_limit(self) -> None:
        bal = self._make_balance(1_000_00)
        payout_list = MagicMock()
        payout_list.data = []

        with patch("stripe.Balance.retrieve", return_value=bal), \
             patch("stripe.Payout.list", return_value=payout_list) as mock_list:
            obtener_auditoria_financiera()

        mock_list.assert_called_once_with(limit=PAYOUT_LIMIT)

    def test_balance_error_returns_not_ok(self) -> None:
        import stripe as stripe_mod
        with patch("stripe.Balance.retrieve", side_effect=stripe_mod.error.StripeError("fail")):
            result = obtener_auditoria_financiera()
        self.assertFalse(result["ok"])
        self.assertIn("Error al leer Balance", result["error"])

    def test_payout_error_returns_not_ok(self) -> None:
        import stripe as stripe_mod
        bal = self._make_balance()
        with patch("stripe.Balance.retrieve", return_value=bal), \
             patch("stripe.Payout.list", side_effect=stripe_mod.error.StripeError("payout fail")):
            result = obtener_auditoria_financiera()
        self.assertFalse(result["ok"])
        self.assertIn("Error al listar Payouts", result["error"])

    def test_sk_passed_directly(self) -> None:
        """La clave puede pasarse directamente sin depender del entorno."""
        bal = self._make_balance(0)
        payout_list = MagicMock()
        payout_list.data = []

        with patch("stripe.Balance.retrieve", return_value=bal), \
             patch("stripe.Payout.list", return_value=payout_list):
            result = obtener_auditoria_financiera(sk="sk_test_explicit")

        self.assertTrue(result["ok"])

    def test_no_hardcoded_key_in_module(self) -> None:
        """El módulo no debe contener ninguna clave sk_live_ hardcodeada (solo placeholders en docs)."""
        import auditoria_financiera as mod
        import re
        import inspect
        source = inspect.getsource(mod)
        # A real key has many characters after sk_live_ prefix — reject anything longer than a placeholder
        hardcoded = re.findall(r"sk_live_[A-Za-z0-9]{20,}", source)
        self.assertEqual(hardcoded, [], f"Clave(s) hardcodeada(s) encontrada(s): {hardcoded}")


if __name__ == "__main__":
    unittest.main()
