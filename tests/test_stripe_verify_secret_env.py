"""Tests for stripe_verify_secret_env.py — env resolution."""

import os
import sys
import unittest
from unittest.mock import patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from stripe_verify_secret_env import resolve_stripe_secret

class TestResolveStripeSecret(unittest.TestCase):
    def test_prefers_fr_key(self) -> None:
        with patch.dict(os.environ, {
            "STRIPE_SECRET_KEY_FR": "sk_fr_123",
            "STRIPE_SECRET_KEY_NUEVA": "sk_nueva_456",
            "STRIPE_SECRET_KEY": "sk_base_789"
        }, clear=True):
            self.assertEqual(resolve_stripe_secret(), "sk_fr_123")

    def test_falls_back_to_nueva_key(self) -> None:
        with patch.dict(os.environ, {
            "STRIPE_SECRET_KEY_NUEVA": "sk_nueva_456",
            "STRIPE_SECRET_KEY": "sk_base_789"
        }, clear=True):
            self.assertEqual(resolve_stripe_secret(), "sk_nueva_456")

    def test_falls_back_to_base_key(self) -> None:
        with patch.dict(os.environ, {
            "STRIPE_SECRET_KEY": " sk_base_789 "
        }, clear=True):
            self.assertEqual(resolve_stripe_secret(), "sk_base_789")

    def test_ignores_empty_strings(self) -> None:
        with patch.dict(os.environ, {
            "STRIPE_SECRET_KEY_FR": "  ",
            "STRIPE_SECRET_KEY_NUEVA": "",
            "STRIPE_SECRET_KEY": "sk_base_789"
        }, clear=True):
            self.assertEqual(resolve_stripe_secret(), "sk_base_789")

    def test_returns_empty_when_no_keys_present(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(resolve_stripe_secret(), "")

if __name__ == "__main__":
    unittest.main()
