import unittest
from tryonyou_app import TryOnYouApp

class TestTryOnYouApp(unittest.TestCase):
    def setUp(self):
        self.app = TryOnYouApp()

    def test_get_recommendations(self):
        recs = self.app.get_recommendations()
        self.assertEqual(len(recs), 5)
        self.assertEqual(recs, self.app.inventory[:5])

    def test_add_to_cart_success(self):
        # Adding a valid item (id 101 exists in default inventory)
        result = self.app.add_to_cart(101)
        self.assertTrue(result)
        self.assertIn("cart", self.app.user_session)
        self.assertEqual(self.app.user_session["cart"]["id"], 101)

    def test_add_to_cart_failure(self):
        # Adding an invalid item (id 999 does not exist)
        result = self.app.add_to_cart(999)
        self.assertFalse(result)
        self.assertNotIn("cart", self.app.user_session)

if __name__ == '__main__':
    unittest.main()
