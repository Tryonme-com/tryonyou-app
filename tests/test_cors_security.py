import unittest
from fastapi.testclient import TestClient
from api.index import app

class TestCORSSecurity(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_cors_allowed_origin(self):
        # Allow origins fallback is https://tryonyou.app and http://localhost:5173
        headers = {
            "Origin": "https://tryonyou.app",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "X-Example"
        }
        response = self.client.options("/", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("access-control-allow-origin"), "https://tryonyou.app")

    def test_cors_disallowed_origin(self):
        headers = {
            "Origin": "https://evil.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "X-Example"
        }
        response = self.client.options("/", headers=headers)
        self.assertEqual(response.status_code, 400) # FastAPI will return 400 for bad origin on preflight, or simply not return CORS header
        self.assertIsNone(response.headers.get("access-control-allow-origin"))

if __name__ == "__main__":
    unittest.main()
