"""Tests para api/stripe_handler — Financial Connections TEST/LIVE auto."""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_API = os.path.join(_ROOT, "api")
for _p in (_ROOT, _API):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from stripe_handler import (
    LIVE_MODE,
    TEST_MODE,
    create_financial_connections_session,
    select_financial_connections_credentials,
)


class TestSelectFinancialConnectionsCredentials(unittest.TestCase):
    def test_verified_account_switches_to_live(self) -> None:
        env = {
            "STRIPE_FINANCIAL_CONNECTIONS_LIVE_SECRET_KEY": "sk_live_fc_123",
            "STRIPE_FINANCIAL_CONNECTIONS_TEST_SECRET_KEY": "sk_test_fc_456",
        }
        key, mode = select_financial_connections_credentials(
            {"verified": True, "customer": "cus_123"},
            env=env,
        )
        self.assertEqual(key, "sk_live_fc_123")
        self.assertEqual(mode, LIVE_MODE)

    def test_unverified_account_uses_test(self) -> None:
        env = {
            "STRIPE_FINANCIAL_CONNECTIONS_LIVE_SECRET_KEY": "sk_live_fc_123",
            "STRIPE_FINANCIAL_CONNECTIONS_TEST_SECRET_KEY": "sk_test_fc_456",
        }
        key, mode = select_financial_connections_credentials(
            {"verified": False, "customer": "cus_123"},
            env=env,
        )
        self.assertEqual(key, "sk_test_fc_456")
        self.assertEqual(mode, TEST_MODE)

    def test_verified_status_text_switches_to_live(self) -> None:
        env = {
            "STRIPE_FINANCIAL_CONNECTIONS_LIVE_SECRET_KEY": "sk_live_fc_123",
            "STRIPE_FINANCIAL_CONNECTIONS_TEST_SECRET_KEY": "sk_test_fc_456",
        }
        key, mode = select_financial_connections_credentials(
            {"status": "verified", "customer": "cus_123"},
            env=env,
        )
        self.assertEqual(key, "sk_live_fc_123")
        self.assertEqual(mode, LIVE_MODE)


class TestCreateFinancialConnectionsSession(unittest.TestCase):
    def tearDown(self) -> None:
        os.environ.pop("STRIPE_RUNTIME_ENV", None)

    def test_create_session_in_live_mode_for_verified_account(self) -> None:
        env = {
            "STRIPE_FINANCIAL_CONNECTIONS_LIVE_SECRET_KEY": "sk_live_fc_123",
            "STRIPE_FINANCIAL_CONNECTIONS_TEST_SECRET_KEY": "sk_test_fc_456",
        }
        session_payload = {
            "id": "fcsess_live_123",
            "client_secret": "fcs_test_secret",
            "livemode": True,
        }
        with patch(
            "stripe_handler.stripe.financial_connections.Session.create",
            return_value=session_payload,
        ) as mock_create:
            payload, code = create_financial_connections_session(
                verified_account={"verified": True, "customer": "cus_live_123"},
                return_url="https://tryonyou.app/return",
                env=env,
            )

        self.assertEqual(code, 200)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["mode"], LIVE_MODE)
        self.assertEqual(payload["session_id"], "fcsess_live_123")
        self.assertEqual(os.environ.get("STRIPE_RUNTIME_ENV"), LIVE_MODE)
        self.assertEqual(
            mock_create.call_args[1]["account_holder"],
            {"type": "customer", "customer": "cus_live_123"},
        )

    def test_create_session_in_test_mode_for_unverified_account(self) -> None:
        env = {
            "STRIPE_FINANCIAL_CONNECTIONS_LIVE_SECRET_KEY": "sk_live_fc_123",
            "STRIPE_FINANCIAL_CONNECTIONS_TEST_SECRET_KEY": "sk_test_fc_456",
        }
        session_payload = {
            "id": "fcsess_test_123",
            "client_secret": "fcs_test_secret",
            "livemode": False,
        }
        with patch(
            "stripe_handler.stripe.financial_connections.Session.create",
            return_value=session_payload,
        ):
            payload, code = create_financial_connections_session(
                verified_account={"verified": False, "customer": "cus_test_123"},
                return_url="https://tryonyou.app/return",
                env=env,
            )

        self.assertEqual(code, 200)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["mode"], TEST_MODE)
        self.assertEqual(os.environ.get("STRIPE_RUNTIME_ENV"), TEST_MODE)

    def test_missing_account_holder_returns_400(self) -> None:
        env = {
            "STRIPE_FINANCIAL_CONNECTIONS_TEST_SECRET_KEY": "sk_test_fc_456",
        }
        payload, code = create_financial_connections_session(
            verified_account={"verified": False},
            return_url="https://tryonyou.app/return",
            env=env,
        )
        self.assertEqual(code, 400)
        self.assertEqual(payload["status"], "error")
        self.assertIn("account_holder", payload["message"])


if __name__ == "__main__":
    unittest.main()
