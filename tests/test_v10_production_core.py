"""Tests for V10_Production_Core manifest properties."""

import sys
import os
import unittest

# Add root directory to path to allow importing from the root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from v10_production_core import V10_Production_Core

class TestV10ProductionCore(unittest.TestCase):
    def test_get_v10_manifest(self):
        core = V10_Production_Core()
        manifest = core.get_v10_manifest()

        self.assertEqual(manifest["status"], "GOLD_MASTER")
        self.assertEqual(manifest["version"], core.version)
        self.assertEqual(manifest["project_id"], core.project_id)
        self.assertEqual(manifest["certification"], "V10_FULL_COMPLIANCE")
        self.assertEqual(manifest["store"], "Galeries Lafayette Haussmann")
        self.assertEqual(manifest["features"], ["Zero_Return_Fit", "Multi_Lang_FR_EN_ES", "Cloud_Studio_Sync"])

if __name__ == "__main__":
    unittest.main()
