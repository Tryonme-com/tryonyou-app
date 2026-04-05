"""Tests para PauIntroductionFrench (pau_introduction_french.py).

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

from pau_introduction_french import PauIntroductionFrench


class TestPauIntroductionFrenchInit(unittest.TestCase):
    """Verifica los atributos iniciales de PauIntroductionFrench."""

    def setUp(self) -> None:
        self.pau = PauIntroductionFrench()

    def test_identity(self) -> None:
        self.assertEqual(self.pau.identity, "P.A.U.")

    def test_location(self) -> None:
        self.assertEqual(self.pau.location, "Galeries Lafayette Haussmann")

    def test_tone(self) -> None:
        self.assertEqual(self.pau.tone, "Raffiné et Chaleureux")


class TestDeliverWelcome(unittest.TestCase):
    """Valida el contenido del mensaje de bienvenida."""

    def setUp(self) -> None:
        self.pau = PauIntroductionFrench()
        self.welcome = self.pau.deliver_welcome()

    def test_returns_string(self) -> None:
        self.assertIsInstance(self.welcome, str)

    def test_contains_salutation(self) -> None:
        self.assertIn("Bonjour", self.welcome)

    def test_contains_presentation(self) -> None:
        self.assertIn("Moi, c'est Pau", self.welcome)

    def test_contains_question(self) -> None:
        self.assertIn("comment vous appelez-vous", self.welcome)

    def test_contains_connection(self) -> None:
        self.assertIn("Enchanté de faire votre connaissance", self.welcome)

    def test_contains_mission(self) -> None:
        self.assertIn("personal shopper", self.welcome)

    def test_contains_energy_closing(self) -> None:
        self.assertIn("C'est parti", self.welcome)
        self.assertIn("Vivido", self.welcome)


class TestFormatForDisplay(unittest.TestCase):
    """Verifica la estructura visual generada por _format_for_display."""

    def setUp(self) -> None:
        self.pau = PauIntroductionFrench()

    def test_output_has_newlines(self) -> None:
        welcome = self.pau.deliver_welcome()
        self.assertIn("\n", welcome)

    def test_salutation_on_first_line(self) -> None:
        welcome = self.pau.deliver_welcome()
        first_line = welcome.splitlines()[0]
        self.assertIn("Bonjour", first_line)

    def test_energy_closing_at_end(self) -> None:
        welcome = self.pau.deliver_welcome()
        last_line = welcome.splitlines()[-1]
        self.assertIn("Vivido", last_line)


if __name__ == "__main__":
    unittest.main()
