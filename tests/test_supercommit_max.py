"""Contrato operativo para Supercommit_Max y deployall."""

from __future__ import annotations

import os
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestSupercommitMaxScripts(unittest.TestCase):
    def test_shell_entrypoints_parse(self) -> None:
        scripts = [
            "supercommit_max.sh",
            "SUPERCOMMIT.sh",
            "TRYONYOU_SUPERCOMMIT_MAX.sh",
            "Supercommit_Max",
            "scripts/deployall.sh",
        ]
        for script in scripts:
            with self.subTest(script=script):
                subprocess.run(["bash", "-n", str(ROOT / script)], check=True)

    def test_supercommit_pushes_current_branch(self) -> None:
        text = (ROOT / "supercommit_max.sh").read_text(encoding="utf-8")
        self.assertIn('git push -u origin "$branch_name"', text)

    def test_supercommit_accepts_custom_message_and_free_message(self) -> None:
        text = (ROOT / "supercommit_max.sh").read_text(encoding="utf-8")
        self.assertIn("--msg", text)
        self.assertIn("COMMIT_MSG_RAW", text)

    def test_supercommit_keeps_required_sovereignty_seals(self) -> None:
        text = (ROOT / "supercommit_max.sh").read_text(encoding="utf-8")
        self.assertIn("@CertezaAbsoluta", text)
        self.assertIn("@lo+erestu", text)
        self.assertIn("PCT/EP2025/067317", text)
        self.assertIn("Bajo Protocolo de Soberanía V10 - Founder: Rubén", text)

    def test_legacy_wrapper_does_not_push_main_or_force(self) -> None:
        text = (ROOT / "SUPERCOMMIT.sh").read_text(encoding="utf-8")
        self.assertNotIn("git push origin main", text)
        self.assertNotIn("--force", text)
        self.assertIn("supercommit_max.sh", text)

    def test_deployall_is_package_target(self) -> None:
        self.assertTrue((ROOT / "scripts/deployall.sh").exists())
        package_json = (ROOT / "package.json").read_text(encoding="utf-8")
        self.assertIn('"deployall": "bash scripts/deployall.sh"', package_json)

    def test_env_example_documents_deploy_bot_without_secret(self) -> None:
        text = (ROOT / ".env.example").read_text(encoding="utf-8")
        self.assertIn("TRYONYOU_DEPLOY_BOT_TOKEN=", text)
        self.assertIn("TRYONYOU_DEPLOY_CHAT_ID=", text)
        self.assertNotIn("8788913760:", text)


if __name__ == "__main__":
    os.chdir(ROOT)
    unittest.main()
