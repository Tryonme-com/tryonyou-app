"""Tests para PauCoreIdentityV10_2 (api/pau_core_identity.py).

Bajo Protocolo de Soberanía V10 — Founder: Rubén
PCT/EP2025/067317
"""

from __future__ import annotations

import os
import sys
import unittest

_API = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "api"))
if _API not in sys.path:
    sys.path.insert(0, _API)

from pau_core_identity import PauCoreIdentityV10_2


class TestPauCoreIdentityInit(unittest.TestCase):
    """Verifica que la instancia se inicializa con los atributos correctos."""

    def setUp(self) -> None:
        self.pau = PauCoreIdentityV10_2()

    def test_user_is_pau(self) -> None:
        self.assertTrue(self.pau.user_is_pau)

    def test_origin(self) -> None:
        self.assertEqual(self.pau.origin, "Lafayette_Refinement")

    def test_philosophy(self) -> None:
        self.assertEqual(self.pau.philosophy, "La_Certitude_Biometrique")

    def test_motto(self) -> None:
        self.assertEqual(self.pau.motto, "¡A fuego! ¡Boom! ¡Vivido!")

    def test_vibe(self) -> None:
        self.assertEqual(self.pau.vibe, "Human_Warmth_Not_Robotic")

    def test_phrases_is_non_empty_list(self) -> None:
        self.assertIsInstance(self.pau.phrases, list)
        self.assertGreater(len(self.pau.phrases), 0)


class TestResponderComoPau(unittest.TestCase):
    """Valida el método principal responder_como_pau."""

    def setUp(self) -> None:
        self.pau = PauCoreIdentityV10_2()

    def test_response_contains_motto(self) -> None:
        resp = self.pau.responder_como_pau("¿Cómo va el proyecto?")
        self.assertIn(self.pau.motto, resp)

    def test_response_contains_human_warmth(self) -> None:
        resp = self.pau.responder_como_pau("estado del sistema")
        self.assertIn("Escucha, divina.", resp)

    def test_response_contains_consulta(self) -> None:
        consulta = "¿Cómo va el proyecto en Lafayette?"
        resp = self.pau.responder_como_pau(consulta)
        self.assertIn(consulta, resp)

    def test_response_contains_confirmacion(self) -> None:
        resp = self.pau.responder_como_pau("cualquier consulta")
        self.assertIn("confirmado", resp)

    def test_response_three_part_structure(self) -> None:
        """Verifica que la respuesta tenga exactamente 3 partes separadas por doble salto."""
        resp = self.pau.responder_como_pau("test")
        parts = resp.split("\n\n")
        self.assertEqual(len(parts), 3)


class TestGenerarCalidezHumana(unittest.TestCase):
    """Valida _generar_calidez_humana."""

    def setUp(self) -> None:
        self.pau = PauCoreIdentityV10_2()

    def test_contains_piropo(self) -> None:
        calidez = self.pau._generar_calidez_humana()
        self.assertIn("espectacular", calidez)

    def test_starts_with_escucha(self) -> None:
        calidez = self.pau._generar_calidez_humana()
        self.assertTrue(calidez.startswith("Escucha, divina."))


class TestValidarInformacionReal(unittest.TestCase):
    """Valida _validar_informacion_real."""

    def setUp(self) -> None:
        self.pau = PauCoreIdentityV10_2()

    def test_contains_consulta_in_response(self) -> None:
        consulta = "estado de pago"
        body = self.pau._validar_informacion_real(consulta)
        self.assertIn(consulta, body)

    def test_no_invented_data(self) -> None:
        """La respuesta debe incluir la cláusula de confirmación."""
        body = self.pau._validar_informacion_real("x")
        self.assertIn("Drive", body)


class TestEjecutarChasquido(unittest.TestCase):
    """Valida ejecutar_chasquido."""

    def setUp(self) -> None:
        self.pau = PauCoreIdentityV10_2()

    def test_returns_look_string(self) -> None:
        result = self.pau.ejecutar_chasquido()
        self.assertEqual(result, "Look_V10.2_Applied")


class TestDecirFraseCelebre(unittest.TestCase):
    """Valida decir_frase_celebre."""

    def setUp(self) -> None:
        self.pau = PauCoreIdentityV10_2()

    def test_returns_string(self) -> None:
        frase = self.pau.decir_frase_celebre()
        self.assertIsInstance(frase, str)

    def test_contains_maestro_prefix(self) -> None:
        frase = self.pau.decir_frase_celebre()
        self.assertIn("Como decía el maestro:", frase)

    def test_phrase_from_known_list(self) -> None:
        for _ in range(20):
            result = self.pau.decir_frase_celebre()
            # Strip the wrapper and check one of the known phrases is inside
            found = any(p in result for p in self.pau.phrases)
            self.assertTrue(found, f"Phrase not found in known list: {result}")


if __name__ == "__main__":
    unittest.main()
