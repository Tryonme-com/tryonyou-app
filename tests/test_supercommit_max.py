from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestSupercommitMaxStaticGuards(unittest.TestCase):
    def test_supercommit_never_pushes_main_or_git_add_dot(self) -> None:
        script = (ROOT / "supercommit_max.sh").read_text(encoding="utf-8")
        legacy = (ROOT / "SUPERCOMMIT.sh").read_text(encoding="utf-8")

        self.assertNotIn("git push origin main", script)
        self.assertNotIn("git push origin main", legacy)
        self.assertNotIn("git add .", script)
        self.assertNotIn("git add .", legacy)
        self.assertIn('git push -u origin "$branch"', script)
        self.assertIn("git add -u -- .", script)
        self.assertIn("git ls-files --others --exclude-standard -z", script)

    def test_entrypoints_delegate_to_safe_script(self) -> None:
        entrypoint = ROOT / "Supercommit_Max"
        wrapper = ROOT / "TRYONYOU_SUPERCOMMIT_MAX.sh"

        self.assertTrue(entrypoint.is_file())
        self.assertIn('exec "$ROOT/supercommit_max.sh" "$@"', entrypoint.read_text(encoding="utf-8"))
        self.assertIn('exec "$ROOT/Supercommit_Max" "$@"', wrapper.read_text(encoding="utf-8"))

    def test_deploy_bot_uses_environment_only(self) -> None:
        script = (ROOT / "supercommit_max.sh").read_text(encoding="utf-8")

        self.assertIn("TRYONYOU_DEPLOY_BOT_TOKEN", script)
        self.assertIn("TRYONYOU_DEPLOY_CHAT_ID", script)
        self.assertIn("TELEGRAM_BOT_TOKEN", script)
        self.assertIsNone(re.search(r"\d{8,}:[A-Za-z0-9_-]{20,}", script))


if __name__ == "__main__":
    unittest.main()
