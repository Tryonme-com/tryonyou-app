import unittest
from unittest.mock import patch

from api import index


class TestStripeWebhookEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = index.app.test_client()

    def test_missing_signature_header(self):
        with patch.object(index, "STRIPE_ENDPOINT_SECRET", "whsec_test"):
            response = self.client.post("/api/webhook", data=b"{}")

        self.assertEqual(response.status_code, 400)
        self.assertIn("missing signature", response.get_data(as_text=True))

    def test_invalid_payload(self):
        with patch.object(index, "STRIPE_ENDPOINT_SECRET", "whsec_test"):
            with patch("api.index.stripe.Webhook.construct_event", side_effect=ValueError):
                response = self.client.post(
                    "/api/webhook",
                    data=b"{bad json}",
                    headers={"Stripe-Signature": "t=1,v1=fake"},
                )

        self.assertEqual(response.status_code, 400)
        self.assertIn("invalid payload", response.get_data(as_text=True))

    def test_payment_intent_succeeded(self):
        event = {"type": "payment_intent.succeeded", "data": {"object": {"id": "pi_123"}}}
        with patch.object(index, "STRIPE_ENDPOINT_SECRET", "whsec_test"):
            with patch("api.index.stripe.Webhook.construct_event", return_value=event):
                with patch("api.index.print") as print_mock:
                    response = self.client.post(
                        "/api/webhook",
                        data=b"{}",
                        headers={"Stripe-Signature": "t=1,v1=fake"},
                    )

        self.assertEqual(response.status_code, 200)
        self.assertIn("success", response.get_data(as_text=True))
        print_mock.assert_called_with("[tryonyou] Stripe payment_intent.succeeded received", flush=True)


if __name__ == "__main__":
    unittest.main()
