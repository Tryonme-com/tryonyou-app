from __future__ import annotations

import os
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUPERCOMMIT = ROOT / "supercommit_max.sh"
WRAPPER = ROOT / "SUPERCOMMIT.sh"


class TestSupercommitMaxScript(unittest.TestCase):
    def test_bash_syntax(self) -> None:
        subprocess.run(["bash", "-n", str(SUPERCOMMIT)], check=True)
        subprocess.run(["bash", "-n", str(WRAPPER)], check=True)

    def test_uses_safe_staging_and_branch_push(self) -> None:
        source = SUPERCOMMIT.read_text(encoding="utf-8")
        self.assertIn("git ls-files -z --modified --deleted --others --exclude-standard", source)
        self.assertIn('git push -u origin "$BRANCH"', source)
        self.assertIn(".env.example) return 0", source)
        self.assertNotIn("git add -A", source)
        self.assertNotIn("git add .", source)
        self.assertNotIn("git push origin main", source)
        self.assertNotIn("--force", source)

    def test_required_commit_stamps_are_injected(self) -> None:
        source = SUPERCOMMIT.read_text(encoding="utf-8")
        self.assertIn("@CertezaAbsoluta @lo+erestu PCT/EP2025/067317", source)
        self.assertIn("Bajo Protocolo de Soberanía V10 - Founder: Rubén", source)
        self.assertIn("append_required_stamps", source)

    def test_notification_uses_environment_without_prompt_token(self) -> None:
        source = SUPERCOMMIT.read_text(encoding="utf-8")
        self.assertIn("TRYONYOU_DEPLOY_BOT_TOKEN", source)
        self.assertIn("TRYONYOU_DEPLOY_CHAT_ID", source)
        self.assertNotIn("8788913760:", source)
        self.assertNotIn("AAE2gS0M8v1", source)

    def test_help_accepts_msg_flag(self) -> None:
        env = os.environ.copy()
        env["PATH"] = env.get("PATH", "")
        result = subprocess.run(
            ["bash", str(SUPERCOMMIT), "--help"],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("--msg TEXT", result.stdout)


if __name__ == "__main__":
    unittest.main()
