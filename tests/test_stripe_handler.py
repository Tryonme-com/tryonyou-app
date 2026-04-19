"""Tests for api/stripe_handler — billing meters, PaymentIntent, Invoice."""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

import stripe

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_API = os.path.join(_ROOT, "api")
for _p in (_ROOT, _API):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from stripe_handler import (
    SIREN,
    _resolve_customer_from_session,
    create_invoice,
    create_payment_intent,
    record_billing_meter_event,
)


class TestResolveCustomerFromSession(unittest.TestCase):
    def test_returns_none_for_none_context(self) -> None:
        self.assertIsNone(_resolve_customer_from_session(None))

    def test_returns_none_for_empty_context(self) -> None:
        self.assertIsNone(_resolve_customer_from_session({}))

    def test_prefers_stripe_customer_id(self) -> None:
        ctx = {
            "stripe_customer_id": "cus_abc",
            "customer_id": "cus_fallback",
            "customer": "cus_last",
        }
        self.assertEqual(_resolve_customer_from_session(ctx), "cus_abc")

    def test_falls_back_to_customer_id(self) -> None:
        ctx = {"customer_id": "cus_fallback"}
        self.assertEqual(_resolve_customer_from_session(ctx), "cus_fallback")

    def test_falls_back_to_customer(self) -> None:
        ctx = {"customer": "cus_last"}
        self.assertEqual(_resolve_customer_from_session(ctx), "cus_last")

    def test_ignores_empty_strings(self) -> None:
        ctx = {"stripe_customer_id": "", "customer_id": "  ", "customer": "cus_ok"}
        self.assertEqual(_resolve_customer_from_session(ctx), "cus_ok")


class TestRecordBillingMeterEvent(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["STRIPE_SECRET_KEY"] = "sk_test_dummy"

    def tearDown(self) -> None:
        os.environ.pop("STRIPE_SECRET_KEY", None)

    def test_fails_without_customer(self) -> None:
        result = record_billing_meter_event(event_name="mirror_session")
        self.assertFalse(result["ok"])
        self.assertIn("customer", result["error"])

    def test_fails_without_event_name(self) -> None:
        result = record_billing_meter_event(customer="cus_123")
        self.assertFalse(result["ok"])
        self.assertIn("event_name", result["error"])

    def test_resolves_customer_from_session(self) -> None:
        ctx = {"stripe_customer_id": "cus_session"}
        mock_event = MagicMock()
        with patch("stripe_handler.stripe.billing.MeterEvent.create", return_value=mock_event) as mock_create:
            result = record_billing_meter_event(
                event_name="mirror_session",
                session_context=ctx,
            )
        self.assertTrue(result["ok"])
        call_kwargs = mock_create.call_args[1]
        self.assertEqual(call_kwargs["event_name"], "mirror_session")
        self.assertEqual(
            call_kwargs["payload"]["stripe_customer_id"], "cus_session",
        )

    def test_direct_customer_takes_precedence(self) -> None:
        ctx = {"stripe_customer_id": "cus_session"}
        mock_event = MagicMock()
        with patch("stripe_handler.stripe.billing.MeterEvent.create", return_value=mock_event) as mock_create:
            result = record_billing_meter_event(
                customer="cus_direct",
                event_name="mirror_session",
                session_context=ctx,
            )
        self.assertTrue(result["ok"])
        call_kwargs = mock_create.call_args[1]
        self.assertEqual(
            call_kwargs["payload"]["stripe_customer_id"], "cus_direct",
        )

    def test_returns_error_on_stripe_exception(self) -> None:
        err = stripe.error.StripeError("bad request")
        with patch("stripe_handler.stripe.billing.MeterEvent.create", side_effect=err):
            result = record_billing_meter_event(
                customer="cus_123", event_name="mirror_session",
            )
        self.assertFalse(result["ok"])


class TestCreatePaymentIntent(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["STRIPE_SECRET_KEY"] = "sk_test_dummy"

    def tearDown(self) -> None:
        os.environ.pop("STRIPE_SECRET_KEY", None)

    def test_includes_siren_in_metadata(self) -> None:
        mock_pi = MagicMock()
        mock_pi.client_secret = "pi_secret_abc"
        mock_pi.id = "pi_abc"
        with patch("stripe_handler.stripe.PaymentIntent.create", return_value=mock_pi) as mock_create:
            result = create_payment_intent(amount_cents=2_750_000)
        self.assertTrue(result["ok"])
        meta = mock_create.call_args[1]["metadata"]
        self.assertEqual(meta["siren"], SIREN)
        self.assertIn("patent", meta)
        self.assertIn("platform", meta)

    def test_amount_sent_as_integer_cents(self) -> None:
        mock_pi = MagicMock()
        mock_pi.client_secret = "pi_secret"
        mock_pi.id = "pi_id"
        with patch("stripe_handler.stripe.PaymentIntent.create", return_value=mock_pi) as mock_create:
            create_payment_intent(amount_cents=2_250_000)
        self.assertEqual(mock_create.call_args[1]["amount"], 2_250_000)

    def test_currency_is_eur_lowercase(self) -> None:
        mock_pi = MagicMock()
        mock_pi.client_secret = "pi_secret"
        mock_pi.id = "pi_id"
        with patch("stripe_handler.stripe.PaymentIntent.create", return_value=mock_pi) as mock_create:
            create_payment_intent(amount_cents=100, currency="EUR")
        self.assertEqual(mock_create.call_args[1]["currency"], "eur")

    def test_customer_from_session_context(self) -> None:
        mock_pi = MagicMock()
        mock_pi.client_secret = "pi_secret"
        mock_pi.id = "pi_id"
        ctx = {"customer_id": "cus_ctx"}
        with patch("stripe_handler.stripe.PaymentIntent.create", return_value=mock_pi) as mock_create:
            create_payment_intent(
                amount_cents=100, session_context=ctx,
            )
        self.assertEqual(mock_create.call_args[1]["customer"], "cus_ctx")


class TestCreateInvoice(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["STRIPE_SECRET_KEY"] = "sk_test_dummy"

    def tearDown(self) -> None:
        os.environ.pop("STRIPE_SECRET_KEY", None)

    def test_fails_without_customer(self) -> None:
        result = create_invoice()
        self.assertFalse(result["ok"])
        self.assertIn("customer", result["error"])

    def test_includes_siren_in_metadata(self) -> None:
        mock_inv = MagicMock()
        mock_inv.id = "in_abc"
        with patch("stripe_handler.stripe.Invoice.create", return_value=mock_inv) as mock_create:
            result = create_invoice(customer="cus_123")
        self.assertTrue(result["ok"])
        meta = mock_create.call_args[1]["metadata"]
        self.assertEqual(meta["siren"], SIREN)

    def test_customer_from_session_context(self) -> None:
        mock_inv = MagicMock()
        mock_inv.id = "in_ctx"
        ctx = {"stripe_customer_id": "cus_session"}
        with patch("stripe_handler.stripe.Invoice.create", return_value=mock_inv) as mock_create:
            result = create_invoice(session_context=ctx)
        self.assertTrue(result["ok"])
        self.assertEqual(mock_create.call_args[1]["customer"], "cus_session")


if __name__ == "__main__":
    unittest.main()
