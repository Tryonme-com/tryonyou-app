"""Reglas de integración Peacock_Core / Zero-Size (unittest estándar)."""

from __future__ import annotations

import os
import sys
import unittest

_API = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "api"))
if _API not in sys.path:
    sys.path.insert(0, _API)

from peacock_core import PILOT_COLLECTION, ZERO_SIZE_LATENCY_BUDGET_MS, is_webhook_destination_forbidden

_PILOT_KEYS = {"drapeCoefficient", "weightGSM", "elasticityPct", "recoveryPct", "frictionCoefficient"}


class TestPilotCollection(unittest.TestCase):
    def test_has_five_entries(self) -> None:
        self.assertEqual(len(PILOT_COLLECTION), 5)

    def test_all_ids_present(self) -> None:
        for key in ("eg0", "eg1", "eg2", "eg3", "eg4"):
            self.assertIn(key, PILOT_COLLECTION)

    def test_each_entry_has_required_keys(self) -> None:
        for fabric_id, props in PILOT_COLLECTION.items():
            self.assertEqual(
                set(props.keys()),
                _PILOT_KEYS,
                msg=f"Fabric entry '{fabric_id}' is missing required keys",
            )

    def test_all_values_are_numeric(self) -> None:
        for fabric_id, props in PILOT_COLLECTION.items():
            for k, v in props.items():
                self.assertIsInstance(
                    v, (int, float),
                    msg=f"PILOT_COLLECTION['{fabric_id}']['{k}'] is not numeric",
                )

    def test_eg0_silk_haussmann_values(self) -> None:
        eg0 = PILOT_COLLECTION["eg0"]
        self.assertAlmostEqual(eg0["drapeCoefficient"], 0.85)
        self.assertAlmostEqual(eg0["weightGSM"], 60)
        self.assertAlmostEqual(eg0["elasticityPct"], 12)
        self.assertAlmostEqual(eg0["recoveryPct"], 95)
        self.assertAlmostEqual(eg0["frictionCoefficient"], 0.22)

    def test_eg3_tech_shell_has_lowest_drape(self) -> None:
        drapes = {k: v["drapeCoefficient"] for k, v in PILOT_COLLECTION.items()}
        self.assertEqual(min(drapes, key=drapes.get), "eg3")

    def test_eg4_cashmere_cloud_highest_elasticity(self) -> None:
        elasticities = {k: v["elasticityPct"] for k, v in PILOT_COLLECTION.items()}
        self.assertEqual(max(elasticities, key=elasticities.get), "eg4")


class TestPeacockCoreIntegration(unittest.TestCase):
    def test_latency_budget_is_25ms(self) -> None:
        self.assertEqual(ZERO_SIZE_LATENCY_BUDGET_MS, 25)

    def test_abvetos_webhook_blocked(self) -> None:
        self.assertTrue(
            is_webhook_destination_forbidden("https://api.abvetos.com/hook/xyz"),
        )
        self.assertTrue(
            is_webhook_destination_forbidden("https://abvetos.com/webhook"),
        )

    def test_make_and_slack_like_urls_allowed(self) -> None:
        self.assertFalse(
            is_webhook_destination_forbidden("https://hook.eu2.make.com/abc"),
        )
        self.assertFalse(
            is_webhook_destination_forbidden("https://hooks.slack.com/services/XX/YY/ZZ"),
        )


if __name__ == "__main__":
    unittest.main()
