from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestIndexHtmlShell(unittest.TestCase):
    def test_gallery_shell_has_no_destructive_lockdown(self) -> None:
        html = (ROOT / "index.html").read_text(encoding="utf-8")

        self.assertIn("<title>TryOnYou × Divineo | Galerie Web Souveraine</title>", html)
        self.assertNotIn("sovereign-protocol-75009-fr", html)
        self.assertNotIn("protocol-deloyaute-75009", html)
        self.assertNotIn("document.documentElement.innerHTML", html)
        self.assertNotIn("ACCÈS RÉVOQUÉ", html)
        self.assertNotIn("33.200", html)

    def test_gallery_shell_keeps_payment_and_root_mount(self) -> None:
        html = (ROOT / "index.html").read_text(encoding="utf-8")

        self.assertIn('id="tryonyou-pay-button"', html)
        self.assertIn('<div id="root"></div>', html)
        self.assertIn('src="/src/main.tsx"', html)


if __name__ == "__main__":
    unittest.main()
