import unittest
import os
from unittest.mock import patch
from inyectar_claves_intelligence import _collect

class TestCollectKeys(unittest.TestCase):
    @patch.dict(os.environ, {}, clear=True)
    def test_empty_environment_returns_empty_dict(self):
        """Test that an empty environment yields an empty dictionary."""
        result = _collect()
        self.assertEqual(result, {})

    @patch.dict(os.environ, {"INJECT_VITE_STRIPE_PUBLIC_KEY": "pk_live_123"}, clear=True)
    def test_primary_alias_sets_canonical_key(self):
        """Test that using the primary alias correctly maps to the canonical key."""
        result = _collect()
        self.assertEqual(result, {"VITE_STRIPE_PUBLIC_KEY": "pk_live_123"})

    @patch.dict(os.environ, {"E50_VITE_STRIPE_PUBLIC_KEY": "pk_live_456"}, clear=True)
    def test_fallback_alias_sets_canonical_key(self):
        """Test that using the fallback alias correctly maps to the canonical key."""
        result = _collect()
        self.assertEqual(result, {"VITE_STRIPE_PUBLIC_KEY": "pk_live_456"})

    @patch.dict(os.environ, {
        "INJECT_VITE_STRIPE_PUBLIC_KEY": "primary_key",
        "E50_VITE_STRIPE_PUBLIC_KEY": "fallback_key"
    }, clear=True)
    def test_priority_handling(self):
        """Test that the primary alias takes precedence over the fallback alias."""
        result = _collect()
        self.assertEqual(result, {"VITE_STRIPE_PUBLIC_KEY": "primary_key"})

    @patch.dict(os.environ, {"INJECT_STRIPE_SECRET_KEY": "   sk_test_abc123   "}, clear=True)
    def test_whitespace_is_stripped(self):
        """Test that whitespace is stripped from the returned values."""
        result = _collect()
        self.assertEqual(result, {"STRIPE_SECRET_KEY": "sk_test_abc123"})

    @patch.dict(os.environ, {"INJECT_VITE_STRIPE_PUBLIC_KEY": "   "}, clear=True)
    def test_empty_whitespace_is_ignored(self):
        """Test that keys evaluating to empty strings after stripping are ignored."""
        result = _collect()
        self.assertEqual(result, {})

if __name__ == '__main__':
    unittest.main()
