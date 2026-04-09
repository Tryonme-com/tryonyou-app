"""Cobertura de salida para validar_omega_v10."""

from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout

from validar_omega_v10 import validar_omega_v10


class TestValidarOmegaV10(unittest.TestCase):
    def test_validar_omega_v10_muestra_bloque_y_estado(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            estado = validar_omega_v10()

        output = buffer.getvalue()
        self.assertIn("AUDITORIA DE DESPLIEGUE OMEGA", output)
        self.assertIn("Via Firestore: CONFIGURADA", output)
        self.assertIn("Google Authenticator: VINCULADO", output)
        self.assertIn("Billing Engine: EJECUTANDO", output)
        self.assertEqual(estado, "ESTADO: Listo para recibir los 27.500 EUR manana.")


if __name__ == "__main__":
    unittest.main()
