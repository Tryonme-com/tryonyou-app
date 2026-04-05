"""Tests para PauMillionDollarInterface (api/pau_interface.py).

Bajo Protocolo de Soberanía V10 — Founder: Rubén
"""

from __future__ import annotations

import os
import sys
import unittest

_API = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "api"))
if _API not in sys.path:
    sys.path.insert(0, _API)

from pau_interface import PauMillionDollarInterface


class TestPauMillionDollarInterfaceAttributes(unittest.TestCase):
    def setUp(self) -> None:
        self.iface = PauMillionDollarInterface()

    def test_brand_is_divineo_v10_2(self) -> None:
        self.assertEqual(self.iface.brand, "Divineo V10.2")

    def test_avatar_id_is_pau_white_peacock_tuxedo(self) -> None:
        self.assertEqual(self.iface.avatar_id, "Pau_White_Peacock_Tuxedo")

    def test_claims_contains_three_languages(self) -> None:
        self.assertIn("es", self.iface.claims)
        self.assertIn("en", self.iface.claims)
        self.assertIn("fr", self.iface.claims)

    def test_claims_es_content(self) -> None:
        self.assertIn("divina", self.iface.claims["es"])

    def test_claims_en_content(self) -> None:
        self.assertIn("divine", self.iface.claims["en"])

    def test_claims_fr_content(self) -> None:
        self.assertIn("divine", self.iface.claims["fr"])


class TestPauMillionDollarInterfaceUIConfig(unittest.TestCase):
    def setUp(self) -> None:
        self.config = PauMillionDollarInterface().get_ui_config()

    def test_background_is_obsidian_black(self) -> None:
        self.assertEqual(self.config["background"], "#0A0A0A")

    def test_accent_color_is_gold_metallic(self) -> None:
        self.assertEqual(self.config["accent_color"], "#D4AF37")

    def test_pau_video_url_is_set(self) -> None:
        self.assertIn("googleusercontent.com", self.config["pau_video_url"])

    def test_video_overlay_mode(self) -> None:
        self.assertEqual(self.config["video_overlay_mode"], "screen")

    def test_border_radius_is_coin_shape(self) -> None:
        self.assertEqual(self.config["border_radius"], "50%")

    def test_animations_field_present(self) -> None:
        self.assertIn("animations", self.config)
        self.assertIn("fade-in", self.config["animations"])

    def test_get_ui_config_returns_dict(self) -> None:
        self.assertIsInstance(self.config, dict)


if __name__ == "__main__":
    unittest.main()
