from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestPaymentLicenseGate(unittest.TestCase):
    def test_spa_renders_payment_terminal_when_license_is_not_active(self) -> None:
        main_tsx = (ROOT / "src" / "main.tsx").read_text(encoding="utf-8")

        self.assertIn("isSovereigntyLicenseActive", main_tsx)
        self.assertIn("PaymentTerminal", main_tsx)
        self.assertIn("!isSovereigntyLicenseActive()", main_tsx)
        self.assertIn("path.startsWith(\"/payment-terminal/\")", main_tsx)

    def test_vercel_routes_preserve_api_and_spa_fallback(self) -> None:
        data = json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))
        routes = data.get("routes", [])

        self.assertEqual(routes[0], {"src": "/api/(.*)", "dest": "/api/index.py"})
        self.assertIn({"src": "/assets/(.*)", "dest": "/assets/$1"}, routes)
        self.assertEqual(routes[-1], {"src": "/(.*)", "dest": "/index.html"})

    def test_edge_middleware_does_not_fetch_same_request_for_passthrough(self) -> None:
        middleware = (ROOT / "middleware.ts").read_text(encoding="utf-8")

        self.assertIn("Response.redirect", middleware)
        self.assertIn("LICENSE_PAID", middleware)
        self.assertIn("VITE_LICENSE_PAID", middleware)
        self.assertNotIn("return fetch(request)", middleware)


if __name__ == "__main__":
    unittest.main()
