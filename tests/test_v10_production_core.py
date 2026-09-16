import unittest
import sys
import os

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from v10_production_core import V10_Production_Core

class TestV10ProductionCore(unittest.TestCase):
    def test_get_v10_manifest(self):
        core = V10_Production_Core()
        manifest = core.get_v10_manifest()

        self.assertEqual(manifest["status"], "GOLD_MASTER")
        self.assertEqual(manifest["version"], "V10.0-CERTIFIED")
        self.assertEqual(manifest["project_id"], "gen-lang-client-0091228222")
        self.assertEqual(manifest["certification"], "V10_FULL_COMPLIANCE")
        self.assertEqual(manifest["store"], "Galeries Lafayette Haussmann")
        self.assertEqual(manifest["features"], ["Zero_Return_Fit", "Multi_Lang_FR_EN_ES", "Cloud_Studio_Sync"])

if __name__ == '__main__':
    unittest.main()
