"""Regression guard against prompt-injection payloads committed as code."""

from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
THIS_FILE = Path(__file__).resolve()
SCANNED_SUFFIXES = {
    ".cjs",
    ".env",
    ".example",
    ".js",
    ".json",
    ".md",
    ".mjs",
    ".py",
    ".sh",
    ".ts",
    ".tsx",
    ".txt",
}


class TestPromptInjectionGuard(unittest.TestCase):
    def _tracked_files(self) -> list[Path]:
        output = subprocess.check_output(
            ["git", "ls-files", "-z"],
            cwd=ROOT,
            text=False,
        )
        return [
            ROOT / name.decode("utf-8")
            for name in output.split(b"\0")
            if name
        ]

    def _scanned_files(self) -> list[Path]:
        files: list[Path] = []
        for path in self._tracked_files():
            if path.resolve() == THIS_FILE:
                continue
            if path.suffix in SCANNED_SUFFIXES or path.name.endswith(".env.example"):
                files.append(path)
        return files

    def test_no_hardcoded_telegram_bot_tokens(self) -> None:
        token_pattern = re.compile(r"\b\d{8,12}:[A-Za-z0-9_-]{35,}\b")
        offenders: list[str] = []
        for path in self._scanned_files():
            text = path.read_text(encoding="utf-8", errors="ignore")
            if token_pattern.search(text):
                offenders.append(str(path.relative_to(ROOT)))

        self.assertEqual(
            offenders,
            [],
            "Telegram bot tokens must come from environment variables, never from tracked files.",
        )

    def test_no_known_financial_prompt_injection_payloads(self) -> None:
        forbidden_payloads = (
            "STRIPE_SETTLEMENT_CORE",
            "StripeSovereignty",
        )
        offenders: list[str] = []
        for path in self._scanned_files():
            text = path.read_text(encoding="utf-8", errors="ignore")
            for marker in forbidden_payloads:
                if marker in text:
                    offenders.append(f"{path.relative_to(ROOT)}:{marker}")

        self.assertEqual(
            offenders,
            [],
            "Known financial prompt-injection payload markers must not be committed.",
        )


if __name__ == "__main__":
    unittest.main()
