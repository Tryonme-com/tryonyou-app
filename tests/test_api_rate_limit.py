import unittest
import time
from unittest.mock import patch
from api.index import _rate_check, _RATE

class TestApiRateLimit(unittest.TestCase):
    def setUp(self):
        # Clear the global dictionary before each test
        _RATE.clear()

    def tearDown(self):
        # Clear the global dictionary after each test
        _RATE.clear()

    @patch('api.index.RATE_WINDOW_S', 0.1)
    @patch('api.index.RATE_MAX', 3)
    @patch('api.index.time.time')
    def test_under_limit(self, mock_time):
        mock_time.return_value = 1000.0
        self.assertTrue(_rate_check('192.168.1.1'))
        self.assertTrue(_rate_check('192.168.1.1'))
        self.assertTrue(_rate_check('192.168.1.1'))

    @patch('api.index.RATE_WINDOW_S', 0.1)
    @patch('api.index.RATE_MAX', 3)
    @patch('api.index.time.time')
    def test_over_limit(self, mock_time):
        mock_time.return_value = 1000.0
        self.assertTrue(_rate_check('192.168.1.1'))
        self.assertTrue(_rate_check('192.168.1.1'))
        self.assertTrue(_rate_check('192.168.1.1'))
        # 4th request in the same window should be blocked
        self.assertFalse(_rate_check('192.168.1.1'))

    @patch('api.index.RATE_WINDOW_S', 0.1)
    @patch('api.index.RATE_MAX', 3)
    @patch('api.index.time.time')
    def test_window_expiration(self, mock_time):
        mock_time.return_value = 1000.0
        self.assertTrue(_rate_check('192.168.1.1'))
        self.assertTrue(_rate_check('192.168.1.1'))
        self.assertTrue(_rate_check('192.168.1.1'))
        self.assertFalse(_rate_check('192.168.1.1'))

        # Fast forward time beyond RATE_WINDOW_S
        mock_time.return_value = 1000.15
        self.assertTrue(_rate_check('192.168.1.1'))

    @patch('api.index.RATE_WINDOW_S', 0.1)
    @patch('api.index.RATE_MAX', 3)
    @patch('api.index.time.time')
    def test_independent_tracking(self, mock_time):
        mock_time.return_value = 1000.0
        self.assertTrue(_rate_check('192.168.1.1'))
        self.assertTrue(_rate_check('192.168.1.1'))
        self.assertTrue(_rate_check('192.168.1.1'))
        self.assertFalse(_rate_check('192.168.1.1'))

        # Different IP should still be allowed
        self.assertTrue(_rate_check('10.0.0.1'))

if __name__ == '__main__':
    unittest.main()
