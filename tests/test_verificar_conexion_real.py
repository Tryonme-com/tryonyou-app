"""Tests para verificar_conexion_real — verificación de intentos de pago."""

from __future__ import annotations

import io
import os
import sys
import unittest
from unittest.mock import patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from verificar_conexion_real import verificar_intentos_pago


class TestVerificarIntentosPago(unittest.TestCase):
    def _capture(self, intentos):
        """Helper: captura stdout al llamar verificar_intentos_pago."""
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            verificar_intentos_pago(intentos)
            return mock_stdout.getvalue()

    # ------------------------------------------------------------------
    # Cabecera
    # ------------------------------------------------------------------

    def test_prints_header(self) -> None:
        output = self._capture([])
        self.assertIn("--- [VERIFICACIÓN DE CONEXIÓN] ---", output)

    # ------------------------------------------------------------------
    # Bancario_Externo
    # ------------------------------------------------------------------

    def test_bancario_externo_prints_aviso(self) -> None:
        pago = {"status": "Bancario_Externo", "emisor": "Empresa SA", "monto": 500}
        output = self._capture([pago])
        self.assertIn("AVISO: El pago de Empresa SA NO pasará por la App de Stripe.", output)

    def test_bancario_externo_prints_motivo(self) -> None:
        pago = {"status": "Bancario_Externo", "emisor": "Empresa SA", "monto": 500}
        output = self._capture([pago])
        self.assertIn("MOTIVO: Transferencia corporativa directa al IBAN.", output)

    def test_bancario_externo_no_error_message(self) -> None:
        pago = {"status": "Bancario_Externo", "emisor": "Empresa SA", "monto": 500}
        output = self._capture([pago])
        self.assertNotIn("ERROR:", output)

    # ------------------------------------------------------------------
    # Pago bloqueado (cualquier otro status)
    # ------------------------------------------------------------------

    def test_otro_status_prints_error(self) -> None:
        pago = {"status": "Pendiente", "emisor": "Cliente X", "monto": 200}
        output = self._capture([pago])
        self.assertIn("ERROR: Pago de 200€ bloqueado por falta de verificación.", output)

    def test_otro_status_no_aviso(self) -> None:
        pago = {"status": "Fallido", "emisor": "Cliente Y", "monto": 99}
        output = self._capture([pago])
        self.assertNotIn("AVISO:", output)

    def test_error_message_contains_monto(self) -> None:
        pago = {"status": "Rechazado", "emisor": "Empresa Z", "monto": 1500}
        output = self._capture([pago])
        self.assertIn("1500€", output)

    # ------------------------------------------------------------------
    # Lista mixta
    # ------------------------------------------------------------------

    def test_mixed_list_processes_all(self) -> None:
        intentos = [
            {"status": "Bancario_Externo", "emisor": "Corp A", "monto": 3000},
            {"status": "Pendiente", "emisor": "Corp B", "monto": 750},
            {"status": "Bancario_Externo", "emisor": "Corp C", "monto": 100},
        ]
        output = self._capture(intentos)
        self.assertIn("AVISO: El pago de Corp A NO pasará por la App de Stripe.", output)
        self.assertIn("ERROR: Pago de 750€ bloqueado por falta de verificación.", output)
        self.assertIn("AVISO: El pago de Corp C NO pasará por la App de Stripe.", output)

    def test_empty_list_only_header(self) -> None:
        output = self._capture([])
        lines = [ln for ln in output.splitlines() if ln.strip()]
        self.assertEqual(lines, ["--- [VERIFICACIÓN DE CONEXIÓN] ---"])


if __name__ == "__main__":
    unittest.main()
