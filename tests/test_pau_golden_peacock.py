"""Pruebas de configuración maestra PAU (Golden Peacock)."""

from __future__ import annotations

import os
import sys
import unittest

_API = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "api"))
if _API not in sys.path:
    sys.path.insert(0, _API)

from peacock_core import SYSTEM_PROMPT, get_pau_response


class TestPauGoldenPeacock(unittest.TestCase):
    def test_system_prompt_mentions_golden_peacock_contract(self) -> None:
        self.assertIn("ACTÚA COMO PAU", SYSTEM_PROMPT)
        self.assertIn("FUNCIONES DEL PILOTO (Golden Peacock)", SYSTEM_PROMPT)
        self.assertIn("Creo que me perdí un poco, ¿te refieres a...?", SYSTEM_PROMPT)

    def test_unknown_request_uses_graceful_recovery_phrase(self) -> None:
        answer = get_pau_response("No sé qué tocar aquí", {})
        self.assertIn("Creo que me perdí un poco, ¿te refieres a", answer)

    def test_reservation_without_confirmation_is_honest(self) -> None:
        answer = get_pau_response(
            "Quiero reservar en probador",
            {"fitting_room_availability": "unknown"},
        )
        self.assertIn("validación real de disponibilidad", answer)
        self.assertIn("respuesta honesta", answer)

    def test_reservation_with_confirmation_advances(self) -> None:
        answer = get_pau_response(
            "resérvame probador para hoy",
            {"fitting_room_availability": "confirmed"},
        )
        self.assertIn("disponibilidad confirmada", answer)

    def test_perfect_selection_uses_product_and_size(self) -> None:
        answer = get_pau_response(
            "añade esto a mi selección perfecta",
            {"product_name": "Balmain Signature Jacket", "size": "M"},
        )
        self.assertIn("Balmain Signature Jacket", answer)
        self.assertIn("talla M", answer)

    def test_response_always_closes_with_human_note(self) -> None:
        answer = get_pau_response("quiero ver combinaciones", {})
        markers = (
            "Matisse",
            "sonrisa de atelier",
            "Picasso",
        )
        found = [marker for marker in markers if marker in answer]
        self.assertEqual(len(found), 1)
        self.assertIn(answer[-1], ".!?", "La respuesta final debe cerrar con puntuación natural.")


if __name__ == "__main__":
    unittest.main()
