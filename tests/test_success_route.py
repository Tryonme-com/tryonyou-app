from __future__ import annotations

import os
import sys
import unittest

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from api.index import app


class TestSuccessRoute(unittest.TestCase):
    def setUp(self) -> None:
        self.prev_status = os.environ.get("JULES_STATUS")
        self.client = app.test_client()

    def tearDown(self) -> None:
        if self.prev_status is None:
            os.environ.pop("JULES_STATUS", None)
        else:
            os.environ["JULES_STATUS"] = self.prev_status

    def test_success_route_returns_operational_payload(self) -> None:
        os.environ["JULES_STATUS"] = "OPERATIONAL"

        resp = self.client.get("/success")

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), {"status": "Full Access Restored"})

    def test_success_route_redirects_to_maintenance_when_not_operational(self) -> None:
        os.environ["JULES_STATUS"] = "DEGRADED"

        resp = self.client.get("/success", follow_redirects=False)

        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.headers["Location"].endswith("/maintenance"))

    def test_maintenance_route_is_accessible(self) -> None:
        resp = self.client.get("/maintenance")

        self.assertEqual(resp.status_code, 503)
        self.assertEqual(resp.get_json(), {"status": "maintenance"})


if __name__ == "__main__":
    unittest.main()
