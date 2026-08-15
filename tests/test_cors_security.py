import os
import sys
import unittest
from unittest.mock import patch

# Fix sys.path to allow imports from root
_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

class TestCorsSecurity(unittest.TestCase):
    def test_main_get_allowed_origins_default(self):
        from main import get_allowed_origins

        with patch.dict(os.environ, {}, clear=True):
            origins = get_allowed_origins()
            self.assertEqual(origins, ["https://tryonyou.app", "http://localhost:5173"])

    def test_main_get_allowed_origins_custom(self):
        from main import get_allowed_origins

        with patch.dict(os.environ, {"E50_CORS_ALLOW_ORIGIN": "https://example.com,http://localhost:8080"}, clear=True):
            origins = get_allowed_origins()
            self.assertEqual(origins, ["https://example.com", "http://localhost:8080"])

    def test_api_index_get_allowed_origins_default(self):
        from api.index import get_allowed_origins

        with patch.dict(os.environ, {}, clear=True):
            origins = get_allowed_origins()
            self.assertEqual(origins, ["https://tryonyou.app", "http://localhost:5173"])

    def test_api_index_get_allowed_origins_custom(self):
        from api.index import get_allowed_origins

        with patch.dict(os.environ, {"E50_CORS_ALLOW_ORIGIN": "https://test.com, https://test2.com"}, clear=True):
            origins = get_allowed_origins()
            self.assertEqual(origins, ["https://test.com", "https://test2.com"])

if __name__ == "__main__":
    unittest.main()
