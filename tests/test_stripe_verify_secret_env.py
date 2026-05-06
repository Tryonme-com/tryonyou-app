"""Tests for stripe_verify_secret_env connection validation."""

from __future__ import annotations

import io
import os
import sys
import unittest
from unittest.mock import patch

import stripe

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import stripe_verify_secret_env


_STRIPE_ENV = {
    "STRIPE_RESTRICTED_KEY": "",
    "STRIPE_SECRET_KEY_FR": "",
    "STRIPE_SECRET_KEY_NUEVA": "",
    "STRIPE_SECRET_KEY": "",
}


class TestVerificarConexion(unittest.TestCase):
    def tearDown(self) -> None:
        stripe.api_key = None

    def test_returns_false_without_secret_key(self) -> None:
        captured = io.StringIO()

        with patch.dict(os.environ, _STRIPE_ENV, clear=False), patch(
            "sys.stderr", captured
        ), patch("stripe.Balance.retrieve") as retrieve:
            ok = stripe_verify_secret_env.verificar_conexion()

        self.assertFalse(ok)
        retrieve.assert_not_called()
        self.assertIn("STRIPE_SECRET_KEY_FR", captured.getvalue())

    def test_returns_true_and_calls_balance_with_fr_secret(self) -> None:
        env = {**_STRIPE_ENV, "STRIPE_SECRET_KEY_FR": "  sk_test_fr  "}

        with patch.dict(os.environ, env, clear=False), patch(
            "stripe.Balance.retrieve", return_value=object()
        ) as retrieve:
            ok = stripe_verify_secret_env.verificar_conexion()

        self.assertTrue(ok)
        self.assertEqual(stripe.api_key, "sk_test_fr")
        retrieve.assert_called_once_with()

    def test_returns_false_on_stripe_error(self) -> None:
        captured = io.StringIO()
        env = {**_STRIPE_ENV, "STRIPE_SECRET_KEY_NUEVA": "sk_test_new"}
        err = stripe.error.StripeError("api unavailable")

        with patch.dict(os.environ, env, clear=False), patch(
            "sys.stderr", captured
        ), patch("stripe.Balance.retrieve", side_effect=err):
            ok = stripe_verify_secret_env.verificar_conexion()

        self.assertFalse(ok)
        self.assertEqual(stripe.api_key, "sk_test_new")
        self.assertIn("Balance.retrieve", captured.getvalue())
        self.assertIn("api unavailable", captured.getvalue())

    def test_resolve_api_key_still_allows_restricted_keys_for_main_flow(self) -> None:
        env = {**_STRIPE_ENV, "STRIPE_RESTRICTED_KEY": "rk_test_restricted"}

        with patch.dict(os.environ, env, clear=False):
            key, kind = stripe_verify_secret_env.resolve_api_key()

        self.assertEqual((key, kind), ("rk_test_restricted", "restricted"))


if __name__ == "__main__":
    unittest.main()
