from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from api.index import ADVBET_PROVIDER, app


class TestEmpirePaymentIntentV11(unittest.TestCase):
    def setUp(self) -> None:
        self.client = app.test_client()
        os.environ.pop("ADVBET_BIOMETRIC_DEEP_LINK_BASE", None)
        os.environ.pop("BIOMETRIC_DEEP_LINK_BASE", None)

    def test_requires_session_and_amount(self) -> None:
        response = self.client.post("/api/v1/empire/payment-intent", json={"session_id": ""})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["status"], "error")

    def test_returns_advbet_deep_link_and_qr_payload(self) -> None:
        with patch(
            "api.index.create_lafayette_checkout",
            return_value={
                "client_secret": "pi_secret_123",
                "payment_intent_id": "pi_live_abc",
                "livemode": True,
            },
        ):
            response = self.client.post(
                "/api/v1/empire/payment-intent",
                json={"session_id": "sess_abc_1234", "amount_eur": 125.0},
            )
        self.assertEqual(response.status_code, 200)
        body = response.json
        self.assertEqual(body["status"], "ok")
        self.assertEqual(body["client_secret"], "pi_secret_123")
        self.assertEqual(body["payment_intent_id"], "pi_live_abc")
        self.assertEqual(body["advbet"]["provider"], ADVBET_PROVIDER)
        self.assertIn("session_id=sess_abc_1234", body["advbet"]["biometric_deep_link"])
        self.assertEqual(body["advbet"]["qr_payload"]["format"], "deep_link")
        self.assertEqual(
            body["advbet"]["qr_payload"]["deep_link"],
            body["advbet"]["biometric_deep_link"],
        )

    def test_uses_env_deep_link_base_when_present(self) -> None:
        os.environ["ADVBET_BIOMETRIC_DEEP_LINK_BASE"] = "https://verify.example.com/bio"
        with patch(
            "api.index.create_lafayette_checkout",
            return_value={
                "client_secret": "pi_secret_abc",
                "payment_intent_id": "pi_live_xyz",
                "livemode": True,
            },
        ):
            response = self.client.post(
                "/api/v1/empire/payment-intent",
                json={"session_id": "sess_live_9999", "amount_eur": 80},
            )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            response.json["advbet"]["biometric_deep_link"].startswith("https://verify.example.com/bio?")
        )

    def test_returns_502_when_payment_intent_fails(self) -> None:
        with patch("api.index.create_lafayette_checkout", return_value=None):
            response = self.client.post(
                "/api/v1/empire/payment-intent",
                json={"session_id": "sess_err_1001", "amount_eur": 50},
            )
        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json["message"], "payment_intent_creation_failed")


if __name__ == "__main__":
    unittest.main()
