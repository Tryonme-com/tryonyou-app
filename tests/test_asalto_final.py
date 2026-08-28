import os
import unittest
from unittest.mock import patch

from asalto_final import _on, asalto_final, build_push_command


class TestAsaltoFinal(unittest.TestCase):
    def test_on_truthy_values(self):
        truthy_values = ["1", "true", "yes", "on", " 1 ", " TRUE ", "YeS"]
        for val in truthy_values:
            with patch.dict(os.environ, {"TEST_VAR": val}, clear=True):
                self.assertTrue(_on("TEST_VAR"), f"Expected True for value: '{val}'")

    def test_on_falsy_values(self):
        falsy_values = ["0", "false", "no", "off", " random ", ""]
        for val in falsy_values:
            with patch.dict(os.environ, {"TEST_VAR": val}, clear=True):
                self.assertFalse(_on("TEST_VAR"), f"Expected False for value: '{val}'")

    def test_on_unset_value(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(_on("UNSET_VAR"), "Expected False when env var is unset")

    def test_build_push_command_never_targets_main_force(self):
        cmd = build_push_command("cursor/sincronizaci-n-b-nker-y-seguridad-bafa")
        self.assertEqual(
            cmd,
            ["git", "push", "-u", "origin", "cursor/sincronizaci-n-b-nker-y-seguridad-bafa"],
        )
        with self.assertRaises(ValueError):
            build_push_command("main", {"E50_FORCE_PUSH": "1"})
        with self.assertRaises(ValueError):
            build_push_command("master", {"E50_FORCE_PUSH": "true"})

    def test_build_push_command_allows_force_only_on_feature_branch(self):
        cmd = build_push_command("feature/safe", {"E50_FORCE_PUSH": "yes"})
        self.assertEqual(cmd, ["git", "push", "-u", "origin", "feature/safe", "--force"])

    def test_asalto_final_skips_push_without_flag(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(asalto_final(), 0)


if __name__ == "__main__":
    unittest.main()
