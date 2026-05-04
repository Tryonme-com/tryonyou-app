from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from api.index import app


class TestRootRouteProtection(unittest.TestCase):
    def setUp(self) -> None:
        self.client = app.test_client()

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
        data = response.json
        self.assertEqual(data["status"], "error")
        self.assertEqual(data["message"], "Not Found")
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "*")

    def test_vercel_routes_forward_mutating_root_to_api(self) -> None:
        vercel_json = Path(_ROOT, "vercel.json")
        data = json.loads(vercel_json.read_text(encoding="utf-8"))
        routes = data.get("routes", [])
        target = next(
            (
                route
                for route in routes
                if route.get("src") == "/"
                and route.get("dest") == "/api/index.py"
                and set(route.get("methods", []))
                == {"POST", "PUT", "PATCH", "DELETE", "OPTIONS"}
            ),
            None,
        )
        self.assertIsNotNone(target)


if __name__ == "__main__":
    unittest.main()
