from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "supercommit_max.sh"


def _script() -> str:
    return SCRIPT.read_text(encoding="utf-8")


class SupercommitMaxScriptTests(unittest.TestCase):
    def test_supercommit_targets_current_branch_not_main(self) -> None:
        script = _script()

        self.assertIn('BRANCH="$(git branch --show-current)"', script)
        self.assertIn('git push -u origin "$BRANCH"', script)
        self.assertNotIn("git push origin main", script)
        self.assertNotIn("git push -f", script)

    def test_supercommit_excludes_sensitive_files(self) -> None:
        script = _script()

        for pattern in (".env|.env.*", "*.pem", "*.key", "logs|logs/*"):
            self.assertIn(pattern, script)
        self.assertIn("git ls-files --others --exclude-standard -z", script)

    def test_supercommit_uses_env_telegram_token_only(self) -> None:
        script = _script()

        self.assertIn("TRYONYOU_DEPLOY_BOT_TOKEN", script)
        self.assertIn("TELEGRAM_BOT_TOKEN", script)
        self.assertNotIn("8788913760:", script)
        self.assertRegex(script, r"https://api\.telegram\.org/bot\$\{token\}/sendMessage")

    def test_supercommit_injects_required_commit_stamps(self) -> None:
        script = _script()

        self.assertIn("@CertezaAbsoluta", script)
        self.assertIn("@lo+erestu", script)
        self.assertIn("PCT/EP2025/067317", script)
        self.assertIn("Bajo Protocolo de Soberanía V10 - Founder: Rubén", script)


if __name__ == "__main__":
    unittest.main()
