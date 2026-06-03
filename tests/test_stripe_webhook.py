import unittest
from unittest.mock import patch, MagicMock

from api.index import app


class TestStripeWebhook(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    @patch("api.index.stripe.Webhook.construct_event")
    @patch("api.index.requests.post")
    @patch("api.index.SLACK_WEBHOOK_URL", "https://hooks.slack.test/services/mock")
    def test_invoice_payment_succeeded_sends_slack(self, mock_post, mock_construct_event):
        mock_construct_event.return_value = {
            "type": "invoice.payment_succeeded",
            "data": {
                "object": {
                    "amount_paid": 1250,
                    "currency": "eur",
                    "description": "Pago de cliente confirmado",
                }
            },
        }
        mock_post.return_value = MagicMock(status_code=200)

        response = self.client.post(
            "/api/webhook",
            data=b'{"id":"evt_123"}',
            headers={"Stripe-Signature": "sig"},
        )

        self.assertEqual(response.status_code, 200)
        mock_post.assert_called_once()
        payload = mock_post.call_args.kwargs["json"]
        self.assertEqual(payload["attachments"][0]["fields"][0]["value"], "12.5 EUR")

    @patch("api.index.stripe.Webhook.construct_event")
    @patch("api.index.requests.post")
    @patch("api.index.SLACK_WEBHOOK_URL", "https://hooks.slack.test/services/mock")
    def test_non_invoice_event_does_not_send_slack(self, mock_post, mock_construct_event):
        mock_construct_event.return_value = {"type": "payment_intent.succeeded", "data": {"object": {}}}

        response = self.client.post(
            "/api/webhook",
            data=b'{"id":"evt_123"}',
            headers={"Stripe-Signature": "sig"},
        )

        self.assertEqual(response.status_code, 200)
        mock_post.assert_not_called()

    @patch("api.index.stripe.Webhook.construct_event", side_effect=ValueError("invalid"))
    def test_invalid_payload_returns_400(self, _mock_construct_event):
        response = self.client.post(
            "/api/webhook",
            data=b"invalid",
            headers={"Stripe-Signature": "sig"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["status"], "invalid payload")


if __name__ == "__main__":
    unittest.main()
