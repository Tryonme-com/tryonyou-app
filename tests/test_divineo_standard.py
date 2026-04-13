"""Cobertura de salida para divineo_standard.py."""

from __future__ import annotations

import unittest

from divineo_standard import ImageAsset, ImageQuality, validate_divineo_standard


class TestValidateDivineoStandard(unittest.TestCase):
    def test_masterpiece_returns_approval(self) -> None:
        asset = ImageAsset(quality=ImageQuality.MASTERPIECE)
        result = validate_divineo_standard(asset)
        self.assertEqual(result, "✅ Aprobado para el Búnker V11")

    def test_premium_raises_exception(self) -> None:
        asset = ImageAsset(quality=ImageQuality.PREMIUM)
        with self.assertRaises(Exception) as ctx:
            validate_divineo_standard(asset)
        self.assertIn("CALIDAD INSUFICIENTE", str(ctx.exception))

    def test_high_raises_exception(self) -> None:
        asset = ImageAsset(quality=ImageQuality.HIGH)
        with self.assertRaises(Exception) as ctx:
            validate_divineo_standard(asset)
        self.assertIn("PURGANDO", str(ctx.exception))

    def test_standard_raises_exception(self) -> None:
        asset = ImageAsset(quality=ImageQuality.STANDARD)
        with self.assertRaises(Exception):
            validate_divineo_standard(asset)

    def test_low_raises_exception(self) -> None:
        asset = ImageAsset(quality=ImageQuality.LOW)
        with self.assertRaises(Exception):
            validate_divineo_standard(asset)

    def test_exception_message_matches_spec(self) -> None:
        asset = ImageAsset(quality=ImageQuality.LOW)
        with self.assertRaises(Exception) as ctx:
            validate_divineo_standard(asset)
        self.assertEqual(
            str(ctx.exception),
            "🚫 CALIDAD INSUFICIENTE PARA EL CEO. PURGANDO.",
        )


if __name__ == "__main__":
    unittest.main()
