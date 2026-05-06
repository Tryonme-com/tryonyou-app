from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "supercommit_max.sh"


class TestSupercommitMax(unittest.TestCase):
    def test_validate_only_stages_safe_files_and_excludes_secrets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init"], cwd=repo, check=True, stdout=subprocess.DEVNULL)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)

            (repo / "safe.txt").write_text("safe\n", encoding="utf-8")
            subprocess.run(["git", "add", "safe.txt"], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True, stdout=subprocess.DEVNULL)

            (repo / "safe.txt").write_text("safe changed\n", encoding="utf-8")
            (repo / "new_script.py").write_text("print('ok')\n", encoding="utf-8")
            (repo / ".env").write_text("SECRET=1\n", encoding="utf-8")
            (repo / "server.key").write_text("private\n", encoding="utf-8")
            (repo / "logs").mkdir()
            (repo / "logs" / "run.log").write_text("token\n", encoding="utf-8")

            env = os.environ.copy()
            env["SUPERCOMMIT_VALIDATE_ONLY"] = "1"
            result = subprocess.run(
                ["bash", str(SCRIPT), "--fast", "--msg", "test"],
                cwd=repo,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            staged = subprocess.check_output(
                ["git", "diff", "--cached", "--name-only"],
                cwd=repo,
                text=True,
            ).splitlines()
            self.assertIn("safe.txt", staged)
            self.assertIn("new_script.py", staged)
            self.assertNotIn(".env", staged)
            self.assertNotIn("server.key", staged)
            self.assertNotIn("logs/run.log", staged)

    def test_commit_message_requires_protocol_seals(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("@CertezaAbsoluta", text)
        self.assertIn("@lo+erestu", text)
        self.assertIn("PCT/EP2025/067317", text)
        self.assertIn("Bajo Protocolo de Soberanía V10 - Founder: Rubén", text)


if __name__ == "__main__":
    unittest.main()
