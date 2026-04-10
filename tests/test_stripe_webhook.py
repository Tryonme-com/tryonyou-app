"""Tests para api/stripe_webhook — verificación de firma y despacho de eventos."""

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

from stripe_webhook import (
    _dispatch,
    _on_checkout_session_completed,
    _on_invoice_paid,
    _on_payment_intent_succeeded,
    handle_webhook,
)


class TestHandleWebhookMissingSecret(unittest.TestCase):
    """Cuando STRIPE_WEBHOOK_SECRET no está configurado."""

    def setUp(self) -> None:
        os.environ.pop("STRIPE_WEBHOOK_SECRET", None)

    def test_returns_500_when_secret_missing(self) -> None:
        result, code = handle_webhook(b"{}", "t=1,v1=abc")
        self.assertEqual(code, 500)
        self.assertEqual(result["status"], "error")
        self.assertIn("webhook_secret_not_configured", result["message"])

    def test_returns_500_when_secret_empty(self) -> None:
        os.environ["STRIPE_WEBHOOK_SECRET"] = ""
        result, code = handle_webhook(b"{}", "t=1,v1=abc")
        self.assertEqual(code, 500)
        self.assertEqual(result["status"], "error")


class TestHandleWebhookInvalidPayload(unittest.TestCase):
    """Payload malformado."""

    def setUp(self) -> None:
        os.environ["STRIPE_WEBHOOK_SECRET"] = "whsec_test_secret"

    def tearDown(self) -> None:
        os.environ.pop("STRIPE_WEBHOOK_SECRET", None)

    def test_returns_400_on_invalid_payload(self) -> None:
        with patch(
            "stripe_webhook.stripe.Webhook.construct_event",
            side_effect=ValueError("invalid payload"),
        ):
            result, code = handle_webhook(b"bad_payload", "t=1,v1=abc")
        self.assertEqual(code, 400)
        self.assertEqual(result["status"], "error")
        self.assertIn("invalid_payload", result["message"])


class TestHandleWebhookInvalidSignature(unittest.TestCase):
    """Firma inválida."""

    def setUp(self) -> None:
        os.environ["STRIPE_WEBHOOK_SECRET"] = "whsec_test_secret"

    def tearDown(self) -> None:
        os.environ.pop("STRIPE_WEBHOOK_SECRET", None)

    def test_returns_400_on_invalid_signature(self) -> None:
        with patch(
            "stripe_webhook.stripe.Webhook.construct_event",
            side_effect=stripe.error.SignatureVerificationError("bad sig", "t=1,v1=abc"),
        ):
            result, code = handle_webhook(b"{}", "t=1,v1=bad")
        self.assertEqual(code, 400)
        self.assertEqual(result["status"], "error")
        self.assertIn("invalid_signature", result["message"])


class TestHandleWebhookCheckoutSessionCompleted(unittest.TestCase):
    """Evento checkout.session.completed procesado correctamente."""

    def setUp(self) -> None:
        os.environ["STRIPE_WEBHOOK_SECRET"] = "whsec_test_secret"

    def tearDown(self) -> None:
        os.environ.pop("STRIPE_WEBHOOK_SECRET", None)

    def _make_mock_event(self, event_type: str, session_data: dict) -> MagicMock:
        mock_event = MagicMock()
        mock_event.get.side_effect = lambda key, default=None: (
            event_type if key == "type" else default
        )
        mock_event.__getitem__ = lambda self, key: (
            {"object": session_data} if key == "data" else None
        )
        return mock_event

    def test_returns_200_for_checkout_session_completed(self) -> None:
        session_data = {
            "id": "cs_test_123",
            "customer_details": {"email": "test@example.com"},
            "amount_total": 12500,
            "currency": "eur",
        }
        mock_event = self._make_mock_event("checkout.session.completed", session_data)
        with patch(
            "stripe_webhook.stripe.Webhook.construct_event",
            return_value=mock_event,
        ):
            result, code = handle_webhook(b"{}", "t=1,v1=valid")
        self.assertEqual(code, 200)
        self.assertEqual(result["status"], "ok")
        self.assertTrue(result["handled"])
        self.assertEqual(result["event"], "checkout.session.completed")
        self.assertEqual(result["session_id"], "cs_test_123")
        self.assertEqual(result["invoice_status"], "SUCCEEDED")
        self.assertEqual(result["customer_email"], "test@example.com")
        self.assertEqual(result["amount_total"], 12500)
        self.assertEqual(result["currency"], "eur")

    def test_unhandled_event_type_returns_200_not_handled(self) -> None:
        mock_event = MagicMock()
        mock_event.get.side_effect = lambda key, default=None: (
            "payment_intent.created" if key == "type" else default
        )
        with patch(
            "stripe_webhook.stripe.Webhook.construct_event",
            return_value=mock_event,
        ):
            result, code = handle_webhook(b"{}", "t=1,v1=valid")
        self.assertEqual(code, 200)
        self.assertEqual(result["status"], "ok")
        self.assertFalse(result["handled"])
        self.assertEqual(result["event"], "payment_intent.created")


class TestOnCheckoutSessionCompleted(unittest.TestCase):
    """Pruebas unitarias del handler _on_checkout_session_completed."""

    def test_extracts_session_id(self) -> None:
        session = {"id": "cs_abc", "customer_details": {}, "amount_total": 1000, "currency": "eur"}
        result, code = _on_checkout_session_completed(session)
        self.assertEqual(result["session_id"], "cs_abc")
        self.assertEqual(code, 200)

    def test_extracts_customer_email(self) -> None:
        session = {
            "id": "cs_abc",
            "customer_details": {"email": "buyer@example.com"},
            "amount_total": 5000,
            "currency": "usd",
        }
        result, _ = _on_checkout_session_completed(session)
        self.assertEqual(result["customer_email"], "buyer@example.com")

    def test_missing_email_returns_empty_string(self) -> None:
        session = {"id": "cs_no_email", "customer_details": {}, "amount_total": 0, "currency": "eur"}
        result, _ = _on_checkout_session_completed(session)
        self.assertEqual(result["customer_email"], "")

    def test_amount_and_currency_extracted(self) -> None:
        session = {
            "id": "cs_xyz",
            "customer_details": {"email": "a@b.com"},
            "amount_total": 9900,
            "currency": "eur",
        }
        result, code = _on_checkout_session_completed(session)
        self.assertEqual(result["amount_total"], 9900)
        self.assertEqual(result["currency"], "eur")
        self.assertEqual(code, 200)

    def test_event_type_in_response(self) -> None:
        session = {"id": "cs_t", "customer_details": {}, "amount_total": 0, "currency": "eur"}
        result, _ = _on_checkout_session_completed(session)
        self.assertEqual(result["event"], "checkout.session.completed")
        self.assertTrue(result["handled"])

    @patch("stripe_webhook.LOGGER.info")
    def test_logs_status_transition_to_succeeded(self, mock_info: MagicMock) -> None:
        session = {
            "id": "cs_log",
            "customer_details": {"email": "log@example.com"},
            "amount_total": 4200,
            "currency": "eur",
        }
        _on_checkout_session_completed(session)
        mock_info.assert_called_once()
        args = mock_info.call_args[0]
        self.assertIn("status=SUCCEEDED", args[0])
        self.assertEqual(args[1], "checkout.session.completed")
        self.assertEqual(args[2], "cs_log")


class TestDispatchSucceededEvents(unittest.TestCase):
    """Pruebas para eventos de Stripe que implican SUCCEEDED."""

    def _make_event(self, event_type: str, object_data: dict) -> MagicMock:
        mock_event = MagicMock()
        mock_event.get.side_effect = lambda key, default=None: (
            event_type if key == "type" else default
        )
        mock_event.__getitem__ = lambda self, key: (
            {"object": object_data} if key == "data" else None
        )
        return mock_event

    def test_dispatch_handles_invoice_paid(self) -> None:
        invoice = {
            "id": "in_123",
            "customer_email": "buyer@example.com",
            "amount_paid": 15000,
            "currency": "eur",
        }
        event = self._make_event("invoice.paid", invoice)
        result, code = _dispatch(event)
        self.assertEqual(code, 200)
        self.assertTrue(result["handled"])
        self.assertEqual(result["invoice_status"], "SUCCEEDED")
        self.assertEqual(result["event"], "invoice.paid")

    def test_dispatch_handles_payment_intent_succeeded(self) -> None:
        payment_intent = {
            "id": "pi_123",
            "invoice": "in_999",
            "receipt_email": "paid@example.com",
            "amount_received": 23000,
            "currency": "usd",
        }
        event = self._make_event("payment_intent.succeeded", payment_intent)
        result, code = _dispatch(event)
        self.assertEqual(code, 200)
        self.assertTrue(result["handled"])
        self.assertEqual(result["invoice_status"], "SUCCEEDED")
        self.assertEqual(result["event"], "payment_intent.succeeded")
        self.assertEqual(result["invoice_id"], "in_999")


class TestSucceededHandlers(unittest.TestCase):
    """Tests unitarios directos de handlers SUCCEEDED."""

    @patch("stripe_webhook.LOGGER.info")
    def test_on_invoice_paid_logs_succeeded(self, mock_info: MagicMock) -> None:
        invoice = {
            "id": "in_log",
            "customer_email": "invoice@example.com",
            "amount_paid": 7600,
            "currency": "eur",
        }
        result, code = _on_invoice_paid(invoice)
        self.assertEqual(code, 200)
        self.assertEqual(result["invoice_status"], "SUCCEEDED")
        mock_info.assert_called_once()
        args = mock_info.call_args[0]
        self.assertEqual(args[1], "invoice.paid")
        self.assertEqual(args[2], "in_log")

    @patch("stripe_webhook.LOGGER.info")
    def test_on_payment_intent_succeeded_logs_succeeded(self, mock_info: MagicMock) -> None:
        payment_intent = {
            "id": "pi_log",
            "invoice": "in_from_pi",
            "receipt_email": "pi@example.com",
            "amount_received": 8200,
            "currency": "eur",
        }
        result, code = _on_payment_intent_succeeded(payment_intent)
        self.assertEqual(code, 200)
        self.assertEqual(result["invoice_status"], "SUCCEEDED")
        self.assertEqual(result["invoice_id"], "in_from_pi")
        mock_info.assert_called_once()
        args = mock_info.call_args[0]
        self.assertEqual(args[1], "payment_intent.succeeded")
        self.assertEqual(args[2], "in_from_pi")


if __name__ == "__main__":
    unittest.main()
