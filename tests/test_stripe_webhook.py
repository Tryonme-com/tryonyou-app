import json
import time
import unittest
from unittest.mock import patch

import stripe

from api.index import app


def _stripe_signature(secret: str, payload: str, timestamp: int) -> str:
    signed_payload = f"{timestamp}.{payload}"
    signature = stripe.WebhookSignature._compute_signature(signed_payload, secret)
    return f"t={timestamp},v1={signature}"


class TestStripeWebhook(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.secret = "whsec_test_xxx"

    def test_rejects_missing_signature_header(self):
        with patch("api.index.ENDPOINT_SECRET", self.secret):
            response = self.client.post("/api/webhook", data=b"{}")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"status": "invalid signature"})

    def test_rejects_invalid_payload(self):
        payload = "not-json"
        timestamp = int(time.time())
        header = _stripe_signature(self.secret, payload, timestamp)

        with patch("api.index.ENDPOINT_SECRET", self.secret):
            response = self.client.post(
                "/api/webhook",
                data=payload.encode("utf-8"),
                headers={"Stripe-Signature": header},
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"status": "invalid payload"})

    def test_accepts_supported_stripe_events(self):
        event_types = (
            "payment_intent.succeeded",
            "payment_intent.payment_failed",
            "checkout.session.completed",
            "charge.refunded",
        )

        for event_type in event_types:
            with self.subTest(event_type=event_type):
                payload = json.dumps(
                    {
                        "id": "evt_test_123",
                        "object": "event",
                        "type": event_type,
                        "data": {
                            "object": {
                                "id": "obj_test_123",
                                "amount_received": 1000,
                                "amount_refunded": 500,
                                "currency": "eur",
                                "customer": "cus_test_123",
                                "last_payment_error": {"message": "Card declined"},
                                "mode": "payment",
                            }
                        },
                    }
                )
                timestamp = int(time.time())
                header = _stripe_signature(self.secret, payload, timestamp)

                with patch("api.index.ENDPOINT_SECRET", self.secret):
                    response = self.client.post(
                        "/api/webhook",
                        data=payload.encode("utf-8"),
                        headers={"Stripe-Signature": header},
                    )

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.get_json(), {"status": "success"})


if __name__ == "__main__":
    unittest.main()
