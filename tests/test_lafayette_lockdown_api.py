"""Tests para bloqueo soberano Lafayette en API Flask."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_API = _ROOT / "api"
for _p in (str(_ROOT), str(_API)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from index import app
from lafayette_lockdown import ULTIMATUM


class TestLafayetteLockdownAPI(unittest.TestCase):
    def setUp(self) -> None:
        self.client = app.test_client()
        self._old_env = {
            "LAFAYETTE_LOCK_ENABLED": os.environ.get("LAFAYETTE_LOCK_ENABLED"),
            "LAFAYETTE_PAYMENT_STATUS": os.environ.get("LAFAYETTE_PAYMENT_STATUS"),
            "LAFAYETTE_CONTRACT_MODE": os.environ.get("LAFAYETTE_CONTRACT_MODE"),
            "QONTO_BALANCE_EUR": os.environ.get("QONTO_BALANCE_EUR"),
        }
        # Evita que el guard 402 global tape los tests específicos de lock Lafayette.
        os.environ["QONTO_BALANCE_EUR"] = "999999.00"

    def tearDown(self) -> None:
        for key, value in self._old_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_iban_transfer_is_blocked_for_lafayette_when_payment_pending(self) -> None:
        os.environ["LAFAYETTE_LOCK_ENABLED"] = "1"
        os.environ["LAFAYETTE_PAYMENT_STATUS"] = "AWAITING_210_3K"
        os.environ["LAFAYETTE_CONTRACT_MODE"] = "ANNUAL_FIXED_RATE"

        response = self.client.post(
            "/api/v1/payment/iban-transfer",
            json={"target": "Galeries Lafayette Haussmann"},
        )

        self.assertEqual(response.status_code, 423)
        body = response.get_json() or {}
        self.assertEqual(body.get("status"), "blocked")
        self.assertEqual(body.get("ultimatum"), ULTIMATUM)

    def test_inauguration_checkout_is_blocked_for_vega_context(self) -> None:
        os.environ["LAFAYETTE_LOCK_ENABLED"] = "1"
        os.environ["LAFAYETTE_PAYMENT_STATUS"] = "AWAITING_210_3K"
        os.environ["LAFAYETTE_CONTRACT_MODE"] = "ANNUAL_FIXED_RATE"

        response = self.client.post(
            "/api/stripe_inauguration_checkout",
            json={"store": "Lafayette Vega"},
        )

        self.assertEqual(response.status_code, 423)
        body = response.get_json() or {}
        self.assertEqual(body.get("message"), "lafayette_lockdown_active")
        self.assertIn("payment_pending", body.get("reasons", []))

    def test_territory_contract_is_blocked_for_lafayette_node(self) -> None:
        os.environ["LAFAYETTE_LOCK_ENABLED"] = "1"
        os.environ["LAFAYETTE_PAYMENT_STATUS"] = "AWAITING_210_3K"
        os.environ["LAFAYETTE_CONTRACT_MODE"] = "ANNUAL_FIXED_RATE"

        response = self.client.post(
            "/api/v1/territory/contracts",
            json={"node_id": "lafayette-haussmann"},
        )

        self.assertEqual(response.status_code, 423)
        body = response.get_json() or {}
        self.assertEqual(body.get("target"), "Galeries Lafayette Haussmann")

    def test_iban_transfer_for_lafayette_unblocks_when_payment_received_and_annual_contract(self) -> None:
        os.environ["LAFAYETTE_LOCK_ENABLED"] = "1"
        os.environ["LAFAYETTE_PAYMENT_STATUS"] = "RECEIVED"
        os.environ["LAFAYETTE_CONTRACT_MODE"] = "ANNUAL_FIXED_RATE"

        response = self.client.post(
            "/api/v1/payment/iban-transfer",
            json={"target": "Galeries Lafayette Haussmann"},
        )

        self.assertNotEqual(response.status_code, 423)


if __name__ == "__main__":
    unittest.main()
