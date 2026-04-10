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
    _reset_runtime_state_for_tests,
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


class TestHandleWebhookPayoutCreated(unittest.TestCase):
    """Evento payout.created dispara fase de saneamiento de servicios."""

    def setUp(self) -> None:
        os.environ["STRIPE_WEBHOOK_SECRET"] = "whsec_test_secret"
        os.environ["MAKE_SERVICE_SANITATION_WEBHOOK_URL"] = "https://hook.make.test/stripe"
        os.environ.pop("SERVICE_SANITATION_APPLE_AMOUNT_EUR", None)
        _reset_runtime_state_for_tests()

    def tearDown(self) -> None:
        os.environ.pop("STRIPE_WEBHOOK_SECRET", None)
        os.environ.pop("MAKE_SERVICE_SANITATION_WEBHOOK_URL", None)
        os.environ.pop("SERVICE_SANITATION_APPLE_AMOUNT_EUR", None)
        _reset_runtime_state_for_tests()

    @patch("stripe_webhook.requests.post")
    def test_dispatches_pending_wix_and_apple_payments(self, mock_post: MagicMock) -> None:
        mock_post.return_value.ok = True
        event = {
            "id": "evt_payout_001",
            "type": "payout.created",
            "data": {
                "object": {
                    "id": "po_123",
                    "amount": 100000,
                    "currency": "eur",
                }
            },
        }

        result, code = _dispatch(event)

        self.assertEqual(code, 200)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["event"], "payout.created")
        self.assertTrue(result["handled"])
        self.assertTrue(result["triggered"])
        self.assertEqual(result["event_id"], "evt_payout_001")
        self.assertEqual(len(result["payments"]), 2)
        self.assertEqual(result["payments"][0]["service"], "Wix")
        self.assertEqual(result["payments"][0]["amount_eur"], 489.0)
        self.assertEqual(result["payments"][1]["service"], "Apple")
        self.assertIn("amount_status", result["payments"][1])
        self.assertEqual(mock_post.call_count, 1)

    @patch("stripe_webhook.requests.post")
    def test_returns_502_if_service_webhook_not_configured(self, mock_post: MagicMock) -> None:
        os.environ.pop("MAKE_SERVICE_SANITATION_WEBHOOK_URL", None)
        os.environ.pop("MAKE_WEBHOOK_URL", None)
        event = {
            "id": "evt_payout_002",
            "type": "payout.created",
            "data": {"object": {"id": "po_456"}},
        }

        result, code = _dispatch(event)

        self.assertEqual(code, 502)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["event"], "payout.created")
        self.assertEqual(mock_post.call_count, 0)

    @patch("stripe_webhook.requests.post")
    def test_returns_502_if_make_webhook_fails(self, mock_post: MagicMock) -> None:
        mock_post.return_value.ok = False
        mock_post.return_value.status_code = 500
        event = {
            "id": "evt_payout_003",
            "type": "payout.created",
            "data": {"object": {"id": "po_789"}},
        }

        result, code = _dispatch(event)

        self.assertEqual(code, 502)
        self.assertEqual(result["status"], "error")
        self.assertIn("service_sanitation_http_500", result["message"])
        self.assertEqual(mock_post.call_count, 1)

    @patch("stripe_webhook.requests.post")
    def test_duplicate_event_id_is_idempotent(self, mock_post: MagicMock) -> None:
        mock_post.return_value.ok = True
        event = {
            "id": "evt_payout_dup",
            "type": "payout.created",
            "data": {"object": {"id": "po_dup"}},
        }

        first_result, first_code = _dispatch(event)
        second_result, second_code = _dispatch(event)

        self.assertEqual(first_code, 200)
        self.assertEqual(second_code, 200)
        self.assertTrue(first_result["triggered"])
        self.assertFalse(second_result["triggered"])
        self.assertTrue(second_result["duplicate"])
        self.assertEqual(mock_post.call_count, 1)

    @patch("stripe_webhook.requests.post")
    def test_apple_amount_from_env(self, mock_post: MagicMock) -> None:
        os.environ["SERVICE_SANITATION_APPLE_AMOUNT_EUR"] = "39,99"
        mock_post.return_value.ok = True
        event = {
            "id": "evt_payout_apple_env",
            "type": "payout.created",
            "data": {"object": {"id": "po_apple"}},
        }

        result, code = _dispatch(event)

        self.assertEqual(code, 200)
        self.assertEqual(result["payments"][1]["service"], "Apple")
        self.assertAlmostEqual(result["payments"][1]["amount_eur"], 39.99, places=2)
        self.assertNotIn("amount_status", result["payments"][1])


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


if __name__ == "__main__":
    unittest.main()
