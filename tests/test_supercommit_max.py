"""Tests for the safe Supercommit_Max shell contract."""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "supercommit_max.sh"
LEGACY_SCRIPT = ROOT / "SUPERCOMMIT.sh"


class TestSupercommitMaxContract(unittest.TestCase):
    def test_validate_only_succeeds(self) -> None:
        result = subprocess.run(
            ["bash", str(SCRIPT), "--validate-only"],
            cwd=ROOT,
            check=False,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Validacion OK", result.stdout)

    def test_unknown_flag_fails(self) -> None:
        result = subprocess.run(
            ["bash", str(SCRIPT), "--does-not-exist"],
            cwd=ROOT,
            check=False,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("Flag no reconocida", result.stderr)

    def test_commit_message_contains_required_stamps(self) -> None:
        content = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("@CertezaAbsoluta", content)
        self.assertIn("@lo+erestu", content)
        self.assertIn("PCT/EP2025/067317", content)
        self.assertIn("Bajo Protocolo de Soberanía V10 - Founder: Rubén", content)

    def test_pushes_current_branch_not_main_literal(self) -> None:
        content = SCRIPT.read_text(encoding="utf-8")

        self.assertIn('git push -u origin "$BRANCH"', content)
        self.assertNotIn("git push origin main", content)
        self.assertNotIn("git push -u origin main", content)

    def test_excludes_local_secrets_from_stage(self) -> None:
        content = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("git ls-files --modified --deleted", content)
        self.assertIn("git ls-files --others --exclude-standard", content)
        self.assertIn('"$1" == ".env.example"', content)
        for pattern in ("*.key", "*.pem", "*.p12", "*.pfx", "*.crt", "logs/*", "node_modules/*", "dist/*"):
            self.assertIn(pattern, content)

    def test_legacy_supercommit_delegates_to_safe_script(self) -> None:
        content = LEGACY_SCRIPT.read_text(encoding="utf-8")

        self.assertIn('exec "$ROOT/supercommit_max.sh" "$@"', content)
        self.assertNotIn("vercel deploy --prod", content)
        self.assertNotIn("git push origin main", content)


if __name__ == "__main__":
    unittest.main()
