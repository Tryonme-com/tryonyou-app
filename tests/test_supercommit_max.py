"""Static tests for Supercommit_Max Bash safety contract."""

from __future__ import annotations

import os
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "supercommit_max.sh"


class TestSupercommitMax(unittest.TestCase):
    def test_bash_syntax_is_valid(self) -> None:
        subprocess.run(["bash", "-n", str(SCRIPT)], check=True)

    def test_mandatory_commit_seals_are_present(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("@CertezaAbsoluta", text)
        self.assertIn("@lo+erestu", text)
        self.assertIn("PCT/EP2025/067317", text)
        self.assertIn("Bajo Protocolo de Soberanía V10 - Founder: Rubén", text)

    def test_sensitive_paths_are_not_staged(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        for token in (".env", ".env.*", "logs/*", "*.pem", "*.key", "*.p12", "*.pfx", "*.crt"):
            self.assertIn(token, text)

    def test_push_uses_designated_current_branch(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('git push -u origin "$branch"', text)
        self.assertIn("git branch --show-current", text)

    def test_bot_token_is_read_from_environment_only(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("TRYONYOU_DEPLOY_BOT_TOKEN", text)
        self.assertIn("TELEGRAM_BOT_TOKEN", text)
        self.assertNotIn("8788913760:", text)


if __name__ == "__main__":
    unittest.main()
