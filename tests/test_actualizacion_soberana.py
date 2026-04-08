"""Tests para ActualizacionSoberana — Núcleo TryOnYou (unittest estándar)."""

from __future__ import annotations

import os
import sys
import unittest

_API = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "api"))
if _API not in sys.path:
    sys.path.insert(0, _API)

from actualizacion_soberana import (
    BALANCE_HOJA,
    FECHA,
    PATENTE,
    ActualizacionSoberana,
)


class TestActualizacionSoberanaInit(unittest.TestCase):
    def setUp(self) -> None:
        self.sistema = ActualizacionSoberana()

    def test_fecha(self) -> None:
        self.assertEqual(self.sistema.fecha, "2026-04-08")

    def test_patente(self) -> None:
        self.assertEqual(self.sistema.patente, "PCT/EP2025/067317")

    def test_balance_hoja(self) -> None:
        self.assertAlmostEqual(self.sistema.balance_hoja, 1791.50, places=2)

    def test_module_constants_match(self) -> None:
        self.assertEqual(FECHA, self.sistema.fecha)
        self.assertEqual(PATENTE, self.sistema.patente)
        self.assertAlmostEqual(BALANCE_HOJA, self.sistema.balance_hoja, places=2)


class TestVerificarPresencia(unittest.TestCase):
    def setUp(self) -> None:
        self.sistema = ActualizacionSoberana()

    def test_returns_string(self) -> None:
        result = self.sistema.verificar_presencia()
        self.assertIsInstance(result, str)

    def test_response_contains_style_quote(self) -> None:
        result = self.sistema.verificar_presencia()
        self.assertIn("La moda se démode, le style jamais.", result)

    def test_response_contains_response_prefix(self) -> None:
        result = self.sistema.verificar_presencia()
        self.assertIn("RÉPONSE:", result)

    def test_response_contains_divineo(self) -> None:
        result = self.sistema.verificar_presencia()
        self.assertIn("divineo", result)

    def test_prints_pau_messages(self) -> None:
        import io
        from contextlib import redirect_stdout

        buf = io.StringIO()
        with redirect_stdout(buf):
            self.sistema.verificar_presencia()
        output = buf.getvalue()
        self.assertIn("soberanía", output)
        self.assertIn("certidumbre", output)


class TestBlindajePaloma(unittest.TestCase):
    def setUp(self) -> None:
        self.sistema = ActualizacionSoberana()

    def test_returns_dict(self) -> None:
        result = self.sistema.blindaje_paloma()
        self.assertIsInstance(result, dict)

    def test_ajuste_key(self) -> None:
        result = self.sistema.blindaje_paloma()
        self.assertIn("ajuste", result)
        self.assertIn("99.2%", result["ajuste"])

    def test_don_divin_key(self) -> None:
        result = self.sistema.blindaje_paloma()
        self.assertIn("don_divin", result)
        self.assertIn("Activo", result["don_divin"])

    def test_mensaje_key(self) -> None:
        result = self.sistema.blindaje_paloma()
        self.assertIn("mensaje", result)
        self.assertIn("Bailamos", result["mensaje"])

    def test_all_keys_present(self) -> None:
        result = self.sistema.blindaje_paloma()
        for key in ("ajuste", "don_divin", "mensaje"):
            self.assertIn(key, result)


if __name__ == "__main__":
    unittest.main()
