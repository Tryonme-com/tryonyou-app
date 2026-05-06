"""Tests de seguridad para Supercommit_Max."""

from __future__ import annotations

import os
import unittest
from pathlib import Path


_ROOT = Path(__file__).resolve().parent.parent


class TestSupercommitMaxSafety(unittest.TestCase):
    def test_legacy_wrapper_delegates_to_safe_script(self) -> None:
        wrapper = (_ROOT / "SUPERCOMMIT.sh").read_text(encoding="utf-8")
        self.assertIn('exec "$ROOT/supercommit_max.sh" "$@"', wrapper)
        self.assertNotIn("git push origin main", wrapper)
        self.assertNotIn("vercel deploy --prod", wrapper)

    def test_safe_script_pushes_current_branch_and_excludes_secrets(self) -> None:
        script = (_ROOT / "supercommit_max.sh").read_text(encoding="utf-8")
        self.assertIn('git push -u origin "$BRANCH"', script)
        self.assertIn("Bloqueado: no se opera directamente", script)
        self.assertIn("git ls-files --modified --others --deleted --exclude-standard -z", script)
        self.assertNotIn("git add .", script)
        self.assertNotIn("git push origin main", script)

    def test_canonical_entrypoint_exists(self) -> None:
        entry = _ROOT / "Supercommit_Max"
        self.assertTrue(entry.exists())
        self.assertTrue(os.access(entry, os.X_OK))
        self.assertIn("supercommit_max.sh", entry.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
