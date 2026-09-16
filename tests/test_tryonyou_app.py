import unittest
from tryonyou_app import TryOnYouApp

class TestTryOnYouAppCart(unittest.TestCase):
    def setUp(self):
        self.app = TryOnYouApp()

    def test_add_to_cart_success(self):
        result = self.app.add_to_cart(101)
        self.assertTrue(result)
        self.assertEqual(self.app.user_session.get("cart", {}).get("id"), 101)

    def test_add_to_cart_failure(self):
        result = self.app.add_to_cart(999)
        self.assertFalse(result)
        self.assertNotIn("cart", self.app.user_session)

    def test_get_recommendations(self):
        recs = self.app.get_recommendations()
        self.assertEqual(len(recs), 5)
        self.assertEqual(recs[0]["id"], 101)
