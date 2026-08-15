import unittest
import os
from unittest.mock import patch
import importlib
from fastapi.testclient import TestClient

class TestCORSSecurity(unittest.TestCase):
    def test_allowed_origins(self):
        import main
        importlib.reload(main)
        client = TestClient(main.app)

        headers = {
            "Origin": "https://tryonyou.app",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "X-Requested-With"
        }
        response = client.options("/api/lafayette/metricas", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("access-control-allow-origin", response.headers)
        self.assertEqual(response.headers["access-control-allow-origin"], "https://tryonyou.app")

    def test_disallowed_origin(self):
        import main
        importlib.reload(main)
        client = TestClient(main.app)

        headers = {
            "Origin": "https://evil.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "X-Requested-With"
        }
        response = client.options("/api/lafayette/metricas", headers=headers)
        # Should not allow evil.com
        if "access-control-allow-origin" in response.headers:
            self.assertNotEqual(response.headers["access-control-allow-origin"], "https://evil.com")

    @patch.dict(os.environ, {"E50_CORS_ALLOW_ORIGIN": "https://custom.app,http://localhost:8080"}, clear=True)
    def test_env_var_override(self):
        import main
        importlib.reload(main)
        client = TestClient(main.app)

        # Test custom allowed
        headers = {
            "Origin": "https://custom.app",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "X-Requested-With"
        }
        response = client.options("/api/lafayette/metricas", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("access-control-allow-origin", response.headers)
        self.assertEqual(response.headers["access-control-allow-origin"], "https://custom.app")

        # Test default is NOT allowed since we overrode it
        headers_default = {
            "Origin": "https://tryonyou.app",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "X-Requested-With"
        }
        response_default = client.options("/api/lafayette/metricas", headers=headers_default)
        if "access-control-allow-origin" in response_default.headers:
            self.assertNotEqual(response_default.headers["access-control-allow-origin"], "https://tryonyou.app")

if __name__ == "__main__":
    unittest.main()
