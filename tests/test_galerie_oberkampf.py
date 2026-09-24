from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestGalerieOberkampf(unittest.TestCase):
    def test_web_gallery_names_oberkampf_75011(self) -> None:
        index_html = (ROOT / "client" / "index.html").read_text(encoding="utf-8")
        footer = (ROOT / "client" / "src" / "components" / "sections" / "SiteFooter.tsx").read_text(
            encoding="utf-8"
        )
        hero = (ROOT / "client" / "src" / "components" / "sections" / "Hero.tsx").read_text(encoding="utf-8")

        for source in (index_html, footer, hero):
            self.assertIn("Oberkampf", source)
            self.assertIn("75011", source)

        images = ROOT / "client" / "public" / "images"
        for name in ("gemelo-digital.jpg", "retour-echange.jpg", "mirror-smart.jpg"):
            payload = (images / name).read_bytes()
            self.assertTrue(payload.startswith(b"\xff\xd8"), name)
        for name in ("paloma-lafayette.mp4", "demo-video.mp4"):
            self.assertGreater((images / name).stat().st_size, 1000, name)


if __name__ == "__main__":
    unittest.main()
