import unittest
from fastapi.testclient import TestClient
from main import app

class TestCorsSecurity(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_allowed_origin(self):
        headers = {
            "Origin": "https://abvetos.com",
            "Access-Control-Request-Method": "GET",
        }
        response = self.client.options("/status", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("access-control-allow-origin", response.headers)
        self.assertEqual(response.headers["access-control-allow-origin"], "https://abvetos.com")

    def test_disallowed_origin(self):
        headers = {
            "Origin": "https://evil-attacker.com",
            "Access-Control-Request-Method": "GET",
        }
        response = self.client.options("/status", headers=headers)
        self.assertEqual(response.status_code, 400)
        # Note: Depending on the ASGI server / CORSMiddleware implementation,
        # it might just not return the CORS headers or might return 400.
        # FastAPI/Starlette CORSMiddleware returns 400 Bad Request for disallowed preflight.
        self.assertNotIn("access-control-allow-origin", response.headers)

if __name__ == '__main__':
    unittest.main()
