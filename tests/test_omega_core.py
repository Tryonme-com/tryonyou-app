from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

_BACKEND = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)

from omega_core import app, orchestrator

class TestOmegaCore(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    @patch("omega_core.time.sleep")
    def test_trigger_snap_with_user_id(self, mock_sleep) -> None:
        response = self.client.post("/api/snap", json={"user_id": "VIP_002"})
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertEqual(data["user_id"], "VIP_002")
        self.assertEqual(data["look_applied"], "Balmain Structured Blazer")
        self.assertEqual(data["precision_achieved"], "98.4%")
        self.assertTrue(data["checkout_demo_ref"].startswith("demo_checkout_balmain_"))

    @patch("omega_core.time.sleep")
    def test_trigger_snap_default_user(self, mock_sleep) -> None:
        response = self.client.post("/api/snap", json={})
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertEqual(data["user_id"], "VIP_001")
        self.assertEqual(data["look_applied"], "Balmain Structured Blazer")
        self.assertEqual(data["precision_achieved"], "98.4%")
        self.assertTrue(data["checkout_demo_ref"].startswith("demo_checkout_balmain_"))

    def test_health_endpoint(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data, {"ok": True, "version": orchestrator.version})

if __name__ == "__main__":
    unittest.main()
