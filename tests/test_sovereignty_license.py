"""Tests para sovereignty_license — check_sovereignty_license."""

from __future__ import annotations

import os
import sys
import unittest
from datetime import datetime, timedelta

_API = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "api"))
if _API not in sys.path:
    sys.path.insert(0, _API)

from sovereignty_license import check_sovereignty_license


class TestCheckSovereigntyLicense(unittest.TestCase):
    def test_license_valid_on_start_date(self) -> None:
        """License should be valid on the very start date (day 0)."""
        today = datetime.now().strftime("%Y-%m-%d")
        self.assertTrue(check_sovereignty_license("node-001", today))

    def test_license_valid_within_30_days(self) -> None:
        """License should be valid when fewer than 30 days have passed."""
        recent = (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d")
        self.assertTrue(check_sovereignty_license("node-002", recent))

    def test_license_expired_after_30_days(self) -> None:
        """License should be expired when more than 30 days have passed."""
        old_date = (datetime.now() - timedelta(days=31)).strftime("%Y-%m-%d")
        self.assertFalse(check_sovereignty_license("node-003", old_date))

    def test_license_expired_exactly_at_boundary(self) -> None:
        """License should be expired when exactly 30 days plus one second have passed."""
        expired = (datetime.now() - timedelta(days=30, seconds=1)).strftime("%Y-%m-%d")
        self.assertFalse(check_sovereignty_license("node-004", expired))

    def test_node_id_does_not_affect_result(self) -> None:
        """Different node IDs with the same date should return the same validity."""
        old_date = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")
        self.assertFalse(check_sovereignty_license("node-A", old_date))
        self.assertFalse(check_sovereignty_license("node-B", old_date))

    def test_future_start_date_is_valid(self) -> None:
        """A start date in the future means the license window has not expired."""
        future = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
        self.assertTrue(check_sovereignty_license("node-005", future))


if __name__ == "__main__":
    unittest.main()
