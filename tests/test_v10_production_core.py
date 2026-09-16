import unittest
import sys
import os

# Ensure the root directory is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from v10_production_core import V10_Production_Core

class TestV10ProductionCore(unittest.TestCase):
    def test_get_v10_manifest(self):
        core = V10_Production_Core()
        manifest = core.get_v10_manifest()

        expected_manifest = {
            "status": "GOLD_MASTER",
            "version": core.version,
            "project_id": core.project_id,
            "certification": "V10_FULL_COMPLIANCE",
            "store": "Galeries Lafayette Haussmann",
            "features": ["Zero_Return_Fit", "Multi_Lang_FR_EN_ES", "Cloud_Studio_Sync"],
        }

        self.assertEqual(manifest, expected_manifest)

if __name__ == "__main__":
    unittest.main()
