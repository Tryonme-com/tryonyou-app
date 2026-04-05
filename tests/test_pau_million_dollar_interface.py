"""Tests unitarios para PauMillionDollarInterface (unittest estándar)."""

from __future__ import annotations

import os
import sys
import unittest

_API = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "api"))
if _API not in sys.path:
    sys.path.insert(0, _API)

from pau_million_dollar_interface import PauMillionDollarInterface


class TestPauMillionDollarInterfaceInit(unittest.TestCase):
    def setUp(self) -> None:
        self.pau = PauMillionDollarInterface()

    def test_brand(self) -> None:
        self.assertEqual(self.pau.brand, "Divineo V10.2")

    def test_avatar_id(self) -> None:
        self.assertEqual(self.pau.avatar_id, "Pau_White_Peacock_Tuxedo")

    def test_claims_languages(self) -> None:
        self.assertIn("es", self.pau.claims)
        self.assertIn("en", self.pau.claims)
        self.assertIn("fr", self.pau.claims)

    def test_claims_are_non_empty_strings(self) -> None:
        for lang, text in self.pau.claims.items():
            with self.subTest(lang=lang):
                self.assertIsInstance(text, str)
                self.assertTrue(text.strip(), f"Claim for '{lang}' must not be empty")


class TestPauMillionDollarInterfaceUIConfig(unittest.TestCase):
    def setUp(self) -> None:
        self.config = PauMillionDollarInterface().get_ui_config()

    def test_returns_dict(self) -> None:
        self.assertIsInstance(self.config, dict)

    def test_background_obsidian_black(self) -> None:
        self.assertEqual(self.config["background"], "#0A0A0A")

    def test_accent_color_gold(self) -> None:
        self.assertEqual(self.config["accent_color"], "#D4AF37")

    def test_pau_video_url_present(self) -> None:
        url = self.config["pau_video_url"]
        self.assertIsInstance(url, str)
        self.assertTrue(url.startswith("http"), "pau_video_url must be a valid URL")
        self.assertNotIn("\n", url, "pau_video_url must not contain newlines")

    def test_video_overlay_mode(self) -> None:
        self.assertEqual(self.config["video_overlay_mode"], "screen")

    def test_border_radius_coin_shape(self) -> None:
        self.assertEqual(self.config["border_radius"], "50%")

    def test_animations_fade_in(self) -> None:
        self.assertIn("fade-in", self.config["animations"])

    def test_all_required_keys_present(self) -> None:
        required_keys = {
            "background",
            "accent_color",
            "pau_video_url",
            "video_overlay_mode",
            "border_radius",
            "animations",
        }
        self.assertEqual(required_keys, set(self.config.keys()))


if __name__ == "__main__":
    unittest.main()
