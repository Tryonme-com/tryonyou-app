"""Cobertura de salida para validar_omega_v10."""

from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from validar_omega_v10 import READY_STATUS, REVIEW_STATUS, validar_omega_v10


class TestValidarOmegaV10(unittest.TestCase):
    def _write_json(self, root: Path, name: str, payload: dict) -> None:
        (root / name).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def test_validar_omega_v10_ok_con_identidad_consistente(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_json(
                root,
                "master_omega_vault.json",
                {
                    "identidad": {"patente": "PCT/EP2025/067317", "siret": "94361019600017"},
                    "modulos_activos": {"AUTH_SYNC": "Google-Auth 2.30.0 Verified"},
                },
            )
            self._write_json(
                root,
                "production_manifest.json",
                {"patent": "PCT/EP2025/067317", "siret": "94361019600017"},
            )
            self._write_json(
                root,
                "firebase-applet-config.json",
                {"projectId": "gen-lang-client-0066102635", "apiKey": "x-demo"},
            )
            with patch.dict(os.environ, {"STRIPE_SECRET_KEY": "sk_test_demo"}, clear=False):
                buffer = io.StringIO()
                with redirect_stdout(buffer):
                    estado = validar_omega_v10(root)

        output = buffer.getvalue()
        self.assertIn("Identidad Legal Vault↔Manifest: CONSISTENTE", output)
        self.assertIn("Via Firestore: CONFIGURADA", output)
        self.assertIn("Google Authenticator: VINCULADO", output)
        self.assertIn("Billing Engine: EJECUTANDO", output)
        self.assertEqual(estado, READY_STATUS)

    def test_validar_omega_v10_alerta_si_identidad_inconsistente(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_json(
                root,
                "master_omega_vault.json",
                {
                    "identidad": {"patente": "PCT/EP2025/067317", "siret": "94361019600017"},
                    "modulos_activos": {"AUTH_SYNC": "Google-Auth 2.30.0 Verified"},
                },
            )
            self._write_json(
                root,
                "production_manifest.json",
                {"patent": "PCT/EP2025/000000", "siret": "94361019600017"},
            )
            self._write_json(
                root,
                "firebase-applet-config.json",
                {"projectId": "gen-lang-client-0066102635", "apiKey": ""},
            )
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                estado = validar_omega_v10(root)

        output = buffer.getvalue()
        self.assertIn("Identidad Legal Vault↔Manifest: INCONSISTENTE", output)
        self.assertIn("Via Firestore: PENDIENTE", output)
        self.assertEqual(estado, REVIEW_STATUS)

    def test_validar_omega_v10_muestra_bloque(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            estado = validar_omega_v10()

        output = buffer.getvalue()
        self.assertIn("AUDITORIA DE DESPLIEGUE OMEGA", output)
        self.assertTrue(estado in (READY_STATUS, REVIEW_STATUS))


if __name__ == "__main__":
    unittest.main()
