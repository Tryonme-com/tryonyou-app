"""Tests para pau_despertar_magico.py (PauDespertarMagico V10.2).

@CertezaAbsoluta PCT/EP2025/067317
Bajo Protocolo de Soberanía V10 — Founder: Rubén
"""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from pau_despertar_magico import PauDespertarMagico


class TestPauDespertarMagicoInit(unittest.TestCase):
    """Verifica el estado inicial de PauDespertarMagico."""

    def setUp(self) -> None:
        self.pau = PauDespertarMagico()

    def test_estado_inicial_durmiendo(self) -> None:
        self.assertEqual(self.pau.estado, "DURMIENDO")

    def test_ubicacion_inicial(self) -> None:
        self.assertEqual(self.pau.ubicacion, "RAMA_SUEÑO_ETEREO")

    def test_iluminacion_inicial_penumbra(self) -> None:
        self.assertAlmostEqual(self.pau.iluminacion, 0.1)


class TestPauDespertarMagicoIniciarExperiencia(unittest.TestCase):
    """Valida la secuencia de inicio y transición de estado."""

    def setUp(self) -> None:
        self.pau = PauDespertarMagico()

    def test_estado_cambia_a_despierto(self) -> None:
        self.pau.iniciar_experiencia()
        self.assertEqual(self.pau.estado, "DESPIERTO_Y_LISTO")

    def test_iniciar_experiencia_devuelve_string(self) -> None:
        resultado = self.pau.iniciar_experiencia()
        self.assertIsInstance(resultado, str)

    def test_iniciar_experiencia_contiene_saludo(self) -> None:
        resultado = self.pau.iniciar_experiencia()
        self.assertIn("Pau se inclina con una reverencia", resultado)

    def test_iniciar_experiencia_contiene_piropo(self) -> None:
        resultado = self.pau.iniciar_experiencia()
        self.assertIn("París", resultado)

    def test_iniciar_experiencia_contiene_frase_celebre(self) -> None:
        resultado = self.pau.iniciar_experiencia()
        self.assertIn("sencillez", resultado)

    def test_iniciar_experiencia_contiene_cta(self) -> None:
        resultado = self.pau.iniciar_experiencia()
        self.assertIn("divineo", resultado)

    def test_render_paso_llamado_tres_veces(self) -> None:
        with patch.object(self.pau, "_render_paso") as mock_render:
            self.pau.iniciar_experiencia()
        self.assertEqual(mock_render.call_count, 3)

    def test_secuencia_incluye_abrir_ojos(self) -> None:
        pasos_recibidos: list[dict] = []
        original_render = self.pau._render_paso

        def capture(data):
            pasos_recibidos.append(data)
            return original_render(data)

        with patch.object(self.pau, "_render_paso", side_effect=capture):
            self.pau.iniciar_experiencia()

        acciones = [p["accion"] for p in pasos_recibidos]
        self.assertIn("Abrir_Ojos", acciones)
        self.assertIn("Sacudida_Plumas", acciones)
        self.assertIn("Descenso_Rama", acciones)

    def test_imprime_sincronizando(self) -> None:
        with patch("builtins.print") as mock_print:
            self.pau.iniciar_experiencia()
        args_list = [str(call) for call in mock_print.call_args_list]
        printed = " ".join(args_list)
        self.assertIn("presencia divina", printed)


class TestPauDespertarMagicoSaludoInicial(unittest.TestCase):
    """Valida el contenido del saludo inicial independientemente."""

    def setUp(self) -> None:
        self.pau = PauDespertarMagico()

    def test_saludo_contiene_reverencia(self) -> None:
        saludo = self.pau.saludo_inicial()
        self.assertIn("reverencia", saludo)

    def test_saludo_contiene_paris(self) -> None:
        saludo = self.pau.saludo_inicial()
        self.assertIn("París", saludo)

    def test_saludo_contiene_elegancia(self) -> None:
        saludo = self.pau.saludo_inicial()
        self.assertIn("elegancia", saludo)

    def test_saludo_contiene_boom(self) -> None:
        saludo = self.pau.saludo_inicial()
        self.assertIn("Boom", saludo)


class TestPauDespertarMagicoRenderPaso(unittest.TestCase):
    """_render_paso no debe lanzar excepción con datos válidos."""

    def test_render_paso_no_lanza_excepcion(self) -> None:
        pau = PauDespertarMagico()
        try:
            pau._render_paso({"accion": "test", "efecto": "ninguno"})
        except Exception:
            self.fail("_render_paso lanzó una excepción inesperada")


if __name__ == "__main__":
    unittest.main()
