import unittest
from unittest.mock import patch
import os
import sys

from stripe_verify_secret_env import resolve_stripe_secret

class TestStripeVerifySecretEnv(unittest.TestCase):
    @patch.dict(os.environ, {"STRIPE_SECRET_KEY_FR": " fr_key ", "STRIPE_SECRET_KEY_NUEVA": " nueva_key ", "STRIPE_SECRET_KEY": " key "}, clear=True)
    def test_resolve_stripe_secret_priority_fr(self):
        self.assertEqual(resolve_stripe_secret(), "fr_key")

    @patch.dict(os.environ, {"STRIPE_SECRET_KEY_NUEVA": " nueva_key ", "STRIPE_SECRET_KEY": " key "}, clear=True)
    def test_resolve_stripe_secret_priority_nueva(self):
        self.assertEqual(resolve_stripe_secret(), "nueva_key")

    @patch.dict(os.environ, {"STRIPE_SECRET_KEY": " key "}, clear=True)
    def test_resolve_stripe_secret_priority_default(self):
        self.assertEqual(resolve_stripe_secret(), "key")

    @patch.dict(os.environ, {}, clear=True)
    def test_resolve_stripe_secret_empty(self):
        self.assertEqual(resolve_stripe_secret(), "")

    @patch.dict(os.environ, {"STRIPE_SECRET_KEY_FR": "   ", "STRIPE_SECRET_KEY_NUEVA": " nueva_key "}, clear=True)
    def test_resolve_stripe_secret_empty_string_fallback(self):
        self.assertEqual(resolve_stripe_secret(), "nueva_key")

if __name__ == "__main__":
    unittest.main()
