from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "supercommit_max.sh"


class SupercommitMaxContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.content = SCRIPT.read_text(encoding="utf-8")

    def test_script_has_safe_bash_preamble(self) -> None:
        self.assertTrue(self.content.startswith("#!/usr/bin/env bash\nset -euo pipefail"))

    def test_commit_message_stamps_are_present(self) -> None:
        self.assertIn("@CertezaAbsoluta @lo+erestu PCT/EP2025/067317", self.content)
        self.assertIn("Bajo Protocolo de Soberanía V10 - Founder: Rubén", self.content)

    def test_pushes_current_branch_with_upstream(self) -> None:
        self.assertIn('branch="$(git branch --show-current)"', self.content)
        self.assertIn('git push -u origin "$branch"', self.content)

    def test_excludes_secrets_and_runtime_logs_from_stage(self) -> None:
        self.assertIn("git reset -q -- .env .env.* logs", self.content)
        self.assertIn("'*.pem'", self.content)
        self.assertIn("'*.key'", self.content)

    def test_telegram_uses_environment_only(self) -> None:
        forbidden_literals = ("8788913760:", "AAE2gS0M8v1", "m8I-K1U9Z")
        for literal in forbidden_literals:
            self.assertNotIn(literal, self.content)
        self.assertIn("TRYONYOU_DEPLOY_BOT_TOKEN", self.content)
        self.assertIn("TRYONYOU_DEPLOY_CHAT_ID", self.content)


if __name__ == "__main__":
    unittest.main()
