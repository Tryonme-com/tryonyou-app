from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
WEB_INDEX = ROOT / "src" / "web" / "index.html"


class TestIndexHtmlShell(unittest.TestCase):
    def test_head_starts_with_metadata_not_lockdown_script(self) -> None:
        lines = INDEX.read_text(encoding="utf-8").splitlines()

        self.assertEqual(lines[0], "<!DOCTYPE html>")
        self.assertEqual(lines[1], '<html lang="fr">')
        self.assertEqual(lines[2], "<head>")
        self.assertIn('<meta charset="UTF-8" />', lines[3])

    def test_shell_has_no_destructive_lockdown_copy(self) -> None:
        html = INDEX.read_text(encoding="utf-8")
        forbidden = [
            "ACCÈS RÉVOQUÉ",
            "PREUVE DE SABOTAGE",
            "33.200",
            "document.documentElement.innerHTML",
            "sovereign-protocol-75009-fr",
        ]

        for marker in forbidden:
            with self.subTest(marker=marker):
                self.assertNotIn(marker, html)

    def test_gallery_metadata_uses_oberkampf_identity(self) -> None:
        html = INDEX.read_text(encoding="utf-8")

        self.assertIn("<title>TryOnYou x Divineo</title>", html)
        self.assertIn('name="description"', html)
        self.assertIn("'postalCode':'75011'", html)

    def test_legacy_web_shell_copy_is_spelled_correctly(self) -> None:
        html = WEB_INDEX.read_text(encoding="utf-8")

        self.assertIn("Stirpe Lafayette", html)
        self.assertIn("MIRROR SOVEREIGN V10", html)
        self.assertNotIn("Lafayet", html)
        self.assertNotIn("SOVERAIGN", html)


if __name__ == "__main__":
    unittest.main()
