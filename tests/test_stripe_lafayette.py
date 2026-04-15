"""Tests para el módulo stripe_lafayette — Lafayette pilot PaymentIntent."""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_API = os.path.join(_ROOT, "api")
for _p in (_ROOT, _API):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from stripe_lafayette import create_lafayette_checkout


class TestCreateLafayetteCheckoutLockdown(unittest.TestCase):
    """Bloqueo soberano: no debe crear checkout con Lafayette bloqueado."""

    def setUp(self) -> None:
        self._env_backup = {
            "LAFAYETTE_LOCK_ENABLED": os.environ.get("LAFAYETTE_LOCK_ENABLED"),
            "LAFAYETTE_PAYMENT_STATUS": os.environ.get("LAFAYETTE_PAYMENT_STATUS"),
            "LAFAYETTE_CONTRACT_MODE": os.environ.get("LAFAYETTE_CONTRACT_MODE"),
            "STRIPE_SECRET_KEY": os.environ.get("STRIPE_SECRET_KEY"),
        }

    def tearDown(self) -> None:
        for key, value in self._env_backup.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_returns_none_when_lockdown_active(self) -> None:
        os.environ["LAFAYETTE_LOCK_ENABLED"] = "1"
        os.environ["LAFAYETTE_PAYMENT_STATUS"] = "AWAITING_210_3K"
        os.environ["LAFAYETTE_CONTRACT_MODE"] = "ANNUAL_FIXED_RATE"
        os.environ["STRIPE_SECRET_KEY"] = "sk_live_testfakekey123"

        with patch("stripe_lafayette.stripe.PaymentIntent.create") as mock_create:
            result = create_lafayette_checkout("LAF-BLOCK", 120.00)

        self.assertIsNone(result)
        mock_create.assert_not_called()

    def test_allows_checkout_when_payment_received_and_annual_contract(self) -> None:
        os.environ["LAFAYETTE_LOCK_ENABLED"] = "1"
        os.environ["LAFAYETTE_PAYMENT_STATUS"] = "RECEIVED"
        os.environ["LAFAYETTE_CONTRACT_MODE"] = "ANNUAL_FIXED_RATE"
        os.environ["STRIPE_SECRET_KEY"] = "sk_live_testfakekey123"

        mock_intent = MagicMock()
        mock_intent.client_secret = "pi_unlocked_secret"

        with patch("stripe_lafayette.stripe.PaymentIntent.create", return_value=mock_intent):
            result = create_lafayette_checkout("LAF-OPEN", 120.00)

        self.assertEqual(result, "pi_unlocked_secret")


class TestCreateLafayetteCheckoutNoKey(unittest.TestCase):
    """Cuando la clave Stripe no está configurada correctamente."""

    def setUp(self) -> None:
        os.environ.pop("STRIPE_SECRET_KEY", None)

    def test_returns_none_when_key_missing(self) -> None:
        result = create_lafayette_checkout("LAF-001", 175.50)
        self.assertIsNone(result)

    def test_returns_none_when_key_is_test_key(self) -> None:
        os.environ["STRIPE_SECRET_KEY"] = "sk_test_abc123"
        try:
            result = create_lafayette_checkout("LAF-001", 175.50)
            self.assertIsNone(result)
        finally:
            os.environ.pop("STRIPE_SECRET_KEY", None)

    def test_returns_none_when_key_is_empty(self) -> None:
        os.environ["STRIPE_SECRET_KEY"] = ""
        try:
            result = create_lafayette_checkout("LAF-001", 175.50)
            self.assertIsNone(result)
        finally:
            os.environ.pop("STRIPE_SECRET_KEY", None)


class TestCreateLafayetteCheckoutWithLiveKey(unittest.TestCase):
    """Con una clave sk_live_ válida (usando mock de Stripe)."""

    def setUp(self) -> None:
        self._env_backup = {
            "LAFAYETTE_LOCK_ENABLED": os.environ.get("LAFAYETTE_LOCK_ENABLED"),
            "LAFAYETTE_PAYMENT_STATUS": os.environ.get("LAFAYETTE_PAYMENT_STATUS"),
            "LAFAYETTE_CONTRACT_MODE": os.environ.get("LAFAYETTE_CONTRACT_MODE"),
        }
        os.environ["LAFAYETTE_LOCK_ENABLED"] = "1"
        os.environ["LAFAYETTE_PAYMENT_STATUS"] = "RECEIVED"
        os.environ["LAFAYETTE_CONTRACT_MODE"] = "ANNUAL_FIXED_RATE"

    def _set_live_key(self) -> None:
        os.environ["STRIPE_SECRET_KEY"] = "sk_live_testfakekey123"

    def tearDown(self) -> None:
        os.environ.pop("STRIPE_SECRET_KEY", None)
        for key, value in self._env_backup.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_returns_client_secret_on_success(self) -> None:
        self._set_live_key()
        mock_intent = MagicMock()
        mock_intent.client_secret = "pi_fake_secret_abc"

        with patch("stripe_lafayette.stripe.PaymentIntent.create", return_value=mock_intent):
            result = create_lafayette_checkout("LAF-001", 175.50)

        self.assertEqual(result, "pi_fake_secret_abc")

    def test_amount_converted_to_cents(self) -> None:
        self._set_live_key()
        mock_intent = MagicMock()
        mock_intent.client_secret = "pi_fake_secret_xyz"

        with patch("stripe_lafayette.stripe.PaymentIntent.create", return_value=mock_intent) as mock_create:
            create_lafayette_checkout("LAF-042", 100.00)
            call_kwargs = mock_create.call_args[1]
            self.assertEqual(call_kwargs["amount"], 10000)

    def test_currency_is_eur(self) -> None:
        self._set_live_key()
        mock_intent = MagicMock()
        mock_intent.client_secret = "pi_fake_secret_xyz"

        with patch("stripe_lafayette.stripe.PaymentIntent.create", return_value=mock_intent) as mock_create:
            create_lafayette_checkout("LAF-002", 50.00)
            call_kwargs = mock_create.call_args[1]
            self.assertEqual(call_kwargs["currency"], "eur")

    def test_metadata_contains_session_id(self) -> None:
        self._set_live_key()
        mock_intent = MagicMock()
        mock_intent.client_secret = "pi_fake_secret_xyz"

        with patch("stripe_lafayette.stripe.PaymentIntent.create", return_value=mock_intent) as mock_create:
            create_lafayette_checkout("LAF-099", 200.00)
            call_kwargs = mock_create.call_args[1]
            self.assertEqual(call_kwargs["metadata"]["session_id"], "LAF-099")
            self.assertEqual(call_kwargs["metadata"]["project"], "TryOnYou_Lafayette_Pilot")

    def test_metadata_contains_siren(self) -> None:
        self._set_live_key()
        mock_intent = MagicMock()
        mock_intent.client_secret = "pi_fake_secret_xyz"

        with patch("stripe_lafayette.stripe.PaymentIntent.create", return_value=mock_intent) as mock_create:
            create_lafayette_checkout("LAF-SIREN", 100.00)
            call_kwargs = mock_create.call_args[1]
            self.assertEqual(call_kwargs["metadata"]["siren"], "943 610 196")
            self.assertEqual(call_kwargs["metadata"]["patent"], "PCT/EP2025/067317")
            self.assertEqual(call_kwargs["metadata"]["platform"], "TryOnYou_V10")

    def test_description_contains_session_id(self) -> None:
        self._set_live_key()
        mock_intent = MagicMock()
        mock_intent.client_secret = "pi_fake_secret_xyz"

        with patch("stripe_lafayette.stripe.PaymentIntent.create", return_value=mock_intent) as mock_create:
            create_lafayette_checkout("LAF-007", 175.50)
            call_kwargs = mock_create.call_args[1]
            self.assertIn("LAF-007", call_kwargs["description"])

    def test_returns_none_on_stripe_error(self) -> None:
        self._set_live_key()
        import stripe as stripe_lib

        with patch(
            "stripe_lafayette.stripe.PaymentIntent.create",
            side_effect=stripe_lib.error.StripeError("card_error"),
        ):
            result = create_lafayette_checkout("LAF-ERR", 50.00)

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
