"""Tests for the Stripe Connect seller dashboard API (stripe_connect.py)."""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

_API = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "api"))
if _API not in sys.path:
    sys.path.insert(0, _API)

import stripe_connect as sc


class TestStripeConnectConfig(unittest.TestCase):
    def test_stripe_not_configured_when_no_key(self) -> None:
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("STRIPE_SECRET_KEY", None)
            self.assertFalse(sc._stripe_configured())

    def test_stripe_configured_when_key_present(self) -> None:
        with patch.dict(os.environ, {"STRIPE_SECRET_KEY": "sk_test_abc123"}):
            self.assertTrue(sc._stripe_configured())

    def test_get_stripe_key_returns_env_value(self) -> None:
        with patch.dict(os.environ, {"STRIPE_SECRET_KEY": "sk_test_xyz"}):
            self.assertEqual(sc._get_stripe_key(), "sk_test_xyz")

    def test_get_stripe_key_returns_empty_when_absent(self) -> None:
        env = {k: v for k, v in os.environ.items() if k != "STRIPE_SECRET_KEY"}
        with patch.dict(os.environ, env, clear=True):
            self.assertEqual(sc._get_stripe_key(), "")


class TestPublishRelicRequest(unittest.TestCase):
    def test_valid_relic_request(self) -> None:
        req = sc.PublishRelicRequest(
            seller_id="seller_123",
            name="Reliquia Dorada",
            price_cents=4999,
            description="Una joya única",
        )
        self.assertEqual(req.seller_id, "seller_123")
        self.assertEqual(req.price_cents, 4999)
        self.assertEqual(req.description, "Una joya única")

    def test_relic_request_description_optional(self) -> None:
        req = sc.PublishRelicRequest(
            seller_id="seller_456",
            name="Reliquia Plata",
            price_cents=1000,
        )
        self.assertIsNone(req.description)


class TestOnboardRequest(unittest.TestCase):
    def test_onboard_request_with_account_id(self) -> None:
        req = sc.OnboardRequest(seller_id="s1", account_id="acct_test123")
        self.assertEqual(req.account_id, "acct_test123")

    def test_onboard_request_without_account_id(self) -> None:
        req = sc.OnboardRequest(seller_id="s1")
        self.assertIsNone(req.account_id)


class TestListRelicsNoStripe(unittest.IsolatedAsyncioTestCase):
    async def test_list_relics_returns_empty_when_stripe_not_configured(self) -> None:
        env = {k: v for k, v in os.environ.items() if k != "STRIPE_SECRET_KEY"}
        with patch.dict(os.environ, env, clear=True):
            result = await sc.list_relics()
        self.assertEqual(result, {"products": []})


class TestGetAccountStatusNoStripe(unittest.IsolatedAsyncioTestCase):
    async def test_get_status_raises_503_when_stripe_not_configured(self) -> None:
        from fastapi import HTTPException

        env = {k: v for k, v in os.environ.items() if k != "STRIPE_SECRET_KEY"}
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(HTTPException) as ctx:
                await sc.get_account_status("acct_test123")
        self.assertEqual(ctx.exception.status_code, 503)

    async def test_get_status_raises_400_for_empty_account_id(self) -> None:
        from fastapi import HTTPException

        env = {k: v for k, v in os.environ.items() if k != "STRIPE_SECRET_KEY"}
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(HTTPException):
                await sc.get_account_status("")


if __name__ == "__main__":
    unittest.main()
