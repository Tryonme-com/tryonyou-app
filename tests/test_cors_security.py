import unittest
import os
import importlib
from unittest.mock import patch
from fastapi.testclient import TestClient
import api.index

class TestCorsSecurity(unittest.TestCase):
    def setUp(self):
        # We need to reload the module to ensure it picks up the patched environment.
        # However, to avoid import issues or double initialization that breaks other tests,
        # we will handle the reload within the specific tests.
        pass

    def test_cors_fallback_domains(self):
        """Test that without the env var, CORS defaults to the hardcoded domains."""
        with patch.dict(os.environ, {}, clear=True):
            importlib.reload(api.index)
            client = TestClient(api.index.app)

            # Test allowed origin
            response = client.options("/", headers={
                "Origin": "https://tryonyou.app",
                "Access-Control-Request-Method": "GET"
            })
            self.assertEqual(response.headers.get("access-control-allow-origin"), "https://tryonyou.app")

            # Test rejected origin (FastAPI CORSMiddleware does NOT return the header for unallowed origins)
            response_rejected = client.options("/", headers={
                "Origin": "https://malicious.com",
                "Access-Control-Request-Method": "GET"
            })
            self.assertIsNone(response_rejected.headers.get("access-control-allow-origin"))

    def test_cors_custom_env_domain(self):
        """Test that setting E50_CORS_ALLOW_ORIGIN overrides the defaults."""
        with patch.dict(os.environ, {"E50_CORS_ALLOW_ORIGIN": "https://custom.app,http://localhost:3000"}, clear=True):
            importlib.reload(api.index)
            client = TestClient(api.index.app)

            # Test new allowed origin
            response = client.options("/", headers={
                "Origin": "https://custom.app",
                "Access-Control-Request-Method": "GET"
            })
            self.assertEqual(response.headers.get("access-control-allow-origin"), "https://custom.app")

            # Test another allowed origin from the list
            response2 = client.options("/", headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET"
            })
            self.assertEqual(response2.headers.get("access-control-allow-origin"), "http://localhost:3000")

            # The original fallback domain should now be rejected since the env var overrode it
            response_rejected = client.options("/", headers={
                "Origin": "https://tryonyou.app",
                "Access-Control-Request-Method": "GET"
            })
            self.assertIsNone(response_rejected.headers.get("access-control-allow-origin"))

if __name__ == "__main__":
    unittest.main()
