from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "supercommit_max.sh"


class SupercommitMaxTest(unittest.TestCase):
    def run_script(self, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PATH"] = f"{ROOT}:{env.get('PATH', '')}"
        return subprocess.run(
            ["bash", str(SCRIPT), *args],
            cwd=str(cwd or ROOT),
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def test_bash_syntax_is_valid(self) -> None:
        result = subprocess.run(
            ["bash", "-n", str(SCRIPT)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_unknown_flag(self) -> None:
        result = self.run_script("--unknown")

        self.assertEqual(result.returncode, 2)
        self.assertIn("Flag no reconocida", result.stderr)

    def test_fast_allows_custom_message_and_pushes_current_branch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            remote = Path(tmp) / "remote.git"
            subprocess.run(["git", "init", "--bare", str(remote)], check=True, stdout=subprocess.PIPE)
            subprocess.run(["git", "init", "-b", "feature/test", str(repo)], check=True, stdout=subprocess.PIPE)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
            subprocess.run(["git", "remote", "add", "origin", str(remote)], cwd=repo, check=True)
            (repo / "sample.txt").write_text("ok\n", encoding="utf-8")

            result = self.run_script("--fast", "--msg", "fix: sync bunker gallery", cwd=repo)

            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            log = subprocess.run(
                ["git", "log", "-1", "--pretty=%B"],
                cwd=repo,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            ).stdout
            self.assertIn("fix: sync bunker gallery", log)
            self.assertIn("@CertezaAbsoluta", log)
            self.assertIn("@lo+erestu", log)
            self.assertIn("PCT/EP2025/067317", log)
            self.assertIn("Bajo Protocolo de Soberanía V10 - Founder: Rubén", log)

            branch = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=repo,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            ).stdout.strip()
            self.assertEqual(branch, "feature/test")


if __name__ == "__main__":
    unittest.main()
