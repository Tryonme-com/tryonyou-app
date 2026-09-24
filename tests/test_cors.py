import unittest
import os
from unittest.mock import patch
from fastapi.testclient import TestClient

class TestCORS(unittest.TestCase):
    def setUp(self):
        # We need to reload main or initialize the client with the default environment
        pass

    def test_default_cors_allowed(self):
        # By default, https://tryonyou.app is allowed
        # To ensure isolation, we clear E50_CORS_ALLOW_ORIGIN if it exists
        with patch.dict(os.environ, {}, clear=True):
            # Import main here so it gets the patched environment
            import importlib
            import main
            importlib.reload(main)

            client = TestClient(main.app)
            headers = {
                "Origin": "https://tryonyou.app",
                "Access-Control-Request-Method": "GET"
            }
            response = client.options("/status", headers=headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers.get("access-control-allow-origin"), "https://tryonyou.app")

    def test_default_cors_denied(self):
        with patch.dict(os.environ, {}, clear=True):
            import importlib
            import main
            importlib.reload(main)

            client = TestClient(main.app)
            headers = {
                "Origin": "https://malicious.com",
                "Access-Control-Request-Method": "GET"
            }
            response = client.options("/status", headers=headers)
            self.assertEqual(response.status_code, 400) # FastAPI returns 400 for disallowed CORS on OPTIONS request in some versions, or ignores it. Let's check what TestClient does. Actually it might just not include the ACAO header. Let's test that instead.
            self.assertIsNone(response.headers.get("access-control-allow-origin"))

    def test_custom_cors_env(self):
        # Test with custom environment variable
        with patch.dict(os.environ, {"E50_CORS_ALLOW_ORIGIN": "https://custom.test,http://localhost:3000"}, clear=True):
            import importlib
            import main
            importlib.reload(main)

            client = TestClient(main.app)

            # Should be allowed
            headers1 = {"Origin": "https://custom.test", "Access-Control-Request-Method": "GET"}
            res1 = client.options("/status", headers=headers1)
            self.assertEqual(res1.status_code, 200)
            self.assertEqual(res1.headers.get("access-control-allow-origin"), "https://custom.test")

            # Should be allowed
            headers2 = {"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"}
            res2 = client.options("/status", headers=headers2)
            self.assertEqual(res2.status_code, 200)
            self.assertEqual(res2.headers.get("access-control-allow-origin"), "http://localhost:3000")

            # Should be denied
            headers3 = {"Origin": "https://tryonyou.app", "Access-Control-Request-Method": "GET"}
            res3 = client.options("/status", headers=headers3)
            self.assertIsNone(res3.headers.get("access-control-allow-origin"))

if __name__ == "__main__":
    unittest.main()
