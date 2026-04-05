"""Tests para PauBiometricScanV10_2 (pau_biometric_scan_v10_2.py).

@CertezaAbsoluta @lo+erestu PCT/EP2025/067317
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""

from __future__ import annotations

import os
import sys
import unittest

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from pau_biometric_scan_v10_2 import PauBiometricScanV10_2


class TestPauBiometricScanInit(unittest.TestCase):
    """Verifica la inicialización correcta del escáner biométrico."""

    def setUp(self) -> None:
        self.scan = PauBiometricScanV10_2()

    def test_location_is_paris_haussmann(self) -> None:
        self.assertEqual(self.scan.location, "Paris_Haussmann")

    def test_initial_step_is_biometric_init(self) -> None:
        self.assertEqual(self.scan.step, "BIOMETRIC_INIT")

    def test_motto_contains_paris(self) -> None:
        self.assertIn("Paris", self.scan.motto)


class TestIniciarEscaneoFr(unittest.TestCase):
    """Valida la secuencia de instrucciones en francés."""

    def setUp(self) -> None:
        self.scan = PauBiometricScanV10_2()
        self.result = self.scan.iniciar_escaneo_fr()

    def test_returns_string(self) -> None:
        self.assertIsInstance(self.result, str)

    def test_contains_position_instruction(self) -> None:
        self.assertIn("placez-vous sur la marque", self.result)

    def test_contains_frontal_instruction(self) -> None:
        self.assertIn("Regardez l'écran", self.result)

    def test_contains_profile_instruction(self) -> None:
        self.assertIn("tournez-vous de profil", self.result)

    def test_contains_back_instruction(self) -> None:
        self.assertIn("de dos", self.result)

    def test_contains_confidence_phrase(self) -> None:
        self.assertIn("Faites-moi confiance", self.result)

    def test_contains_vision_phrase(self) -> None:
        self.assertIn("diamant", self.result)

    def test_contains_climax_phrase(self) -> None:
        self.assertIn("Que Paris se prépare", self.result)

    def test_contains_motto(self) -> None:
        self.assertIn(self.scan.motto, self.result)

    def test_default_nombre_usuario_accepted(self) -> None:
        result = self.scan.iniciar_escaneo_fr()
        self.assertIsNotNone(result)

    def test_custom_nombre_usuario_accepted(self) -> None:
        result = self.scan.iniciar_escaneo_fr(nombre_usuario="Sophie")
        self.assertIsNotNone(result)


class TestAnimacionEspejo(unittest.TestCase):
    """Valida los gestos de Pau en cada fase del escaneo."""

    def setUp(self) -> None:
        self.scan = PauBiometricScanV10_2()

    def test_frontal_gesto(self) -> None:
        result = self.scan.animacion_espejo("frontal")
        self.assertIn("Mirada_Directa_Escaneo_Laser", result)

    def test_perfil_gesto(self) -> None:
        result = self.scan.animacion_espejo("perfil")
        self.assertIn("Cabeza_Ladeada_Analisis_Curva", result)

    def test_espalda_gesto(self) -> None:
        result = self.scan.animacion_espejo("espalda")
        self.assertIn("Asentimiento_Autoridad_Pau", result)

    def test_diamante_gesto(self) -> None:
        result = self.scan.animacion_espejo("diamante")
        self.assertIn("Ojos_Brillantes_Dorado", result)

    def test_unknown_fase_returns_none_gesto(self) -> None:
        result = self.scan.animacion_espejo("desconocido")
        self.assertIn("None", result)

    def test_returns_ejecutando_prefix(self) -> None:
        result = self.scan.animacion_espejo("frontal")
        self.assertTrue(result.startswith("Ejecutando gesto:"))


if __name__ == "__main__":
    unittest.main()
