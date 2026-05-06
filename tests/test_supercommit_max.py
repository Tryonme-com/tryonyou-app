from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestSupercommitMax(unittest.TestCase):
    def test_bash_entrypoints_parse(self) -> None:
        for name in ("supercommit_max.sh", "SUPERCOMMIT.sh", "TRYONYOU_SUPERCOMMIT_MAX.sh", "Supercommit_Max"):
            with self.subTest(name=name):
                subprocess.run(["bash", "-n", str(ROOT / name)], check=True)

    def test_legacy_wrapper_does_not_push_main_or_inline_vercel_token(self) -> None:
        content = (ROOT / "SUPERCOMMIT.sh").read_text(encoding="utf-8")
        self.assertNotIn("git push origin main", content)
        self.assertNotIn("--token=$VERCEL_TOKEN", content)
        self.assertIn("supercommit_max.sh", content)

    def test_supercommit_pushes_current_branch_and_blocks_staged_bot_tokens(self) -> None:
        content = (ROOT / "supercommit_max.sh").read_text(encoding="utf-8")
        self.assertIn('git push -u origin "$BRANCH"', content)
        self.assertIn("TRYONYOU_DEPLOY_BOT_TOKEN", content)
        self.assertRegex(content, re.compile(r"\[0-9\]\{8,12\}:"))
        self.assertNotRegex(content, re.compile(r"\d{8,12}:[A-Za-z0-9_-]{20,}"))


if __name__ == "__main__":
    unittest.main()
