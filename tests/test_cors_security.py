import os
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient


class TestCORSSecurity(unittest.TestCase):
    def test_cors_allowed_origin_hardcoded(self):
        # Temporarily patch environment to ensure E50_CORS_ALLOW_ORIGIN is unset
        with patch.dict(os.environ, {}, clear=True):
            # Reload module to apply new env vars
            import importlib
            import api.index

            importlib.reload(api.index)
            client = TestClient(api.index.app)

            # https://tryonyou.app should be allowed by default
            response = client.options(
                "/",
                headers={
                    "Origin": "https://tryonyou.app",
                    "Access-Control-Request-Method": "POST",
                },
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.headers.get("access-control-allow-origin"),
                "https://tryonyou.app",
            )

            # http://malicious.com should NOT be allowed
            response = client.options(
                "/",
                headers={
                    "Origin": "http://malicious.com",
                    "Access-Control-Request-Method": "POST",
                },
            )
            self.assertEqual(
                response.status_code, 400
            )  # FastAPI returns 400 for disallowed CORS origins
            self.assertIsNone(response.headers.get("access-control-allow-origin"))

    def test_cors_allowed_origin_env(self):
        # Patch environment with custom domains
        with patch.dict(
            os.environ,
            {"E50_CORS_ALLOW_ORIGIN": "https://example.com,https://another.com"},
            clear=True,
        ):
            # Reload module to apply new env vars
            import importlib
            import api.index

            importlib.reload(api.index)
            client = TestClient(api.index.app)

            # https://example.com should be allowed
            response = client.options(
                "/",
                headers={
                    "Origin": "https://example.com",
                    "Access-Control-Request-Method": "POST",
                },
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.headers.get("access-control-allow-origin"),
                "https://example.com",
            )

            # Default hardcoded should NOT be allowed when env var is set
            response = client.options(
                "/",
                headers={
                    "Origin": "https://tryonyou.app",
                    "Access-Control-Request-Method": "POST",
                },
            )
            self.assertEqual(response.status_code, 400)
            self.assertIsNone(response.headers.get("access-control-allow-origin"))


if __name__ == "__main__":
    unittest.main()
