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


class TestCreateLafayetteCheckoutNoKey(unittest.TestCase):
    """Cuando la clave Stripe no está configurada correctamente."""

    def setUp(self) -> None:
        os.environ.pop("STRIPE_SECRET_KEY", None)
        os.environ.pop("STRIPE_SECRET_KEY_FR", None)

    def test_returns_none_when_key_missing(self) -> None:
        result = create_lafayette_checkout("LAF-001", 175.50)
        self.assertIsNone(result)

    def test_returns_none_when_key_is_test_key(self) -> None:
        os.environ["STRIPE_SECRET_KEY_FR"] = "sk_test_abc123"
        try:
            result = create_lafayette_checkout("LAF-001", 175.50)
            self.assertIsNone(result)
        finally:
            os.environ.pop("STRIPE_SECRET_KEY_FR", None)

    def test_returns_none_when_key_is_empty(self) -> None:
        os.environ["STRIPE_SECRET_KEY_FR"] = ""
        try:
            result = create_lafayette_checkout("LAF-001", 175.50)
            self.assertIsNone(result)
        finally:
            os.environ.pop("STRIPE_SECRET_KEY_FR", None)


class TestCreateLafayetteCheckoutWithLiveKey(unittest.TestCase):
    """Con una clave sk_live_ válida (usando mock de Stripe)."""

    def _set_live_key(self) -> None:
        os.environ["STRIPE_SECRET_KEY_FR"] = "sk_live_testfakekey123"

    def tearDown(self) -> None:
        os.environ.pop("STRIPE_SECRET_KEY_FR", None)
        os.environ.pop("STRIPE_SECRET_KEY", None)

    def test_returns_client_secret_on_success(self) -> None:
        self._set_live_key()
        mock_intent = MagicMock()
        mock_intent.client_secret = "pi_fake_secret_abc"
        mock_intent.id = "pi_live_fake001"
        mock_intent.livemode = True

        with patch("stripe_lafayette.stripe.PaymentIntent.create", return_value=mock_intent):
            result = create_lafayette_checkout("LAF-001", 175.50)

        assert result is not None
        self.assertEqual(result["client_secret"], "pi_fake_secret_abc")
        self.assertEqual(result["payment_intent_id"], "pi_live_fake001")
        self.assertTrue(result["livemode"])

    def test_amount_converted_to_cents(self) -> None:
        self._set_live_key()
        mock_intent = MagicMock()
        mock_intent.client_secret = "pi_fake_secret_xyz"
        mock_intent.id = "pi_1"
        mock_intent.livemode = True

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
        mock_intent.id = "pi_3"
        mock_intent.livemode = True

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
        mock_intent.id = "pi_5"
        mock_intent.livemode = True

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

    def test_returns_none_when_stripe_returns_test_mode_intent(self) -> None:
        self._set_live_key()
        mock_intent = MagicMock()
        mock_intent.client_secret = "pi_secret_testmode"
        mock_intent.id = "pi_testmode"
        mock_intent.livemode = False

        with patch("stripe_lafayette.stripe.PaymentIntent.create", return_value=mock_intent):
            result = create_lafayette_checkout("LAF-NOT-LIVE", 10.00)

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
