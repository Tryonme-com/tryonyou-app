import unittest
from unittest.mock import patch

from balance_soberana import run_balance_sync
from execute_all import execute_pipeline
from payment_gateway import BLOCKED, READY_FOR_POST, build_gateway_payload


class TestProductionProtocol(unittest.TestCase):
    def test_balance_sync_skips_when_env_is_missing(self):
        with patch.dict("os.environ", {}, clear=True):
            result = run_balance_sync()

        self.assertEqual(result["name"], "balance_soberana")
        self.assertEqual(result["status"], "skipped")
        self.assertIn("PENNYLANE_API_KEY", result["detail"])

    def test_gateway_is_ready_without_error_steps(self):
        payload = build_gateway_payload(
            [
                {"name": "balance_soberana", "status": "success"},
                {"name": "payment_gateway", "status": "skipped"},
            ]
        )

        self.assertEqual(payload["status"], READY_FOR_POST)
        self.assertTrue(payload["ready"])
        self.assertEqual(payload["blocking_steps"], [])

    def test_gateway_blocks_when_any_step_errors(self):
        payload = build_gateway_payload(
            [
                {"name": "balance_soberana", "status": "success"},
                {"name": "payment_gateway", "status": "error"},
            ]
        )

        self.assertEqual(payload["status"], BLOCKED)
        self.assertFalse(payload["ready"])
        self.assertEqual(payload["blocking_steps"], ["payment_gateway"])

    @patch("execute_all.run_balance_sync")
    def test_execute_pipeline_returns_ready_payload(self, mock_run_balance_sync):
        mock_run_balance_sync.return_value = {"name": "balance_soberana", "status": "skipped"}

        payload = execute_pipeline()

        self.assertEqual(payload["status"], READY_FOR_POST)
        self.assertTrue(payload["ready"])


if __name__ == "__main__":
    unittest.main()
