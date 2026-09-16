"""Tests for TRYONYOU OMEGA API."""

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.omega_core import app

client = TestClient(app)

class TestOmegaCore(unittest.TestCase):
    def test_health(self) -> None:
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"ok": True, "version": "10.5-Soberania"})

    @patch("backend.omega_core.time.time")
    @patch("backend.omega_core.time.sleep")
    def test_snap(self, mock_sleep, mock_time) -> None:
        mock_time.return_value = 1234567890.0
        response = client.post("/api/snap", json={"user_id": "VIP_003"})
        self.assertEqual(response.status_code, 200)

        expected_response = {
            "status": "SUCCESS",
            "user_id": "VIP_003",
            "look_applied": "Balmain Structured Blazer",
            "precision_achieved": "98.4%",
            "checkout_demo_ref": "demo_checkout_balmain_1234567890",
        }
        self.assertEqual(response.json(), expected_response)
        self.assertEqual(mock_sleep.call_count, 2)

if __name__ == "__main__":
    unittest.main()
