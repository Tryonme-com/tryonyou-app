from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from api.index import app


class TestRootRouteProtection(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_post_root_is_blocked(self) -> None:
        response = self.client.post(
            "/",
            json={
                "action": "FORCE_PAYOUT",
                "node": "6934",
                "auth": "RUBEN_FOUNDER_8_PERCENT",
            },
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"status": "error", "message": "Not Found"})
        self.assertEqual(response.headers.get("access-control-allow-origin"), "*")

    def test_vercel_rewrites_forward_mutating_root_to_api(self) -> None:
        vercel_json = Path(_ROOT, "vercel.json")
        data = json.loads(vercel_json.read_text(encoding="utf-8"))
        rewrites = data.get("rewrites") or []
        methods = {"POST", "PUT", "PATCH", "DELETE", "OPTIONS"}
        covered: set[str] = set()
        for rule in rewrites:
            if rule.get("source") != "/" or rule.get("destination") != "/api/index.py":
                continue
            for cond in rule.get("has") or []:
                if cond.get("key") == ":method" and cond.get("value") in methods:
                    covered.add(str(cond["value"]))
        self.assertTrue(methods.issubset(covered))


if __name__ == "__main__":
    unittest.main()
