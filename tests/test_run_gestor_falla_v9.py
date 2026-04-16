from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import run_gestor_falla_v9


class TestRunGestorFallaV9(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.input_json = self.base / "input.json"
        self.output_json = self.base / "output.json"
        self.mem_json = self.base / "memory.json"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_normalizar_registro_mapea_campos(self) -> None:
        raw = {
            "payer_name": "Pau",
            "charge_type": "cuota",
            "amount": 100,
            "transaction_id": "TX-100",
            "member_id": "F-001",
            "date": "2026-04-16",
        }
        normalized = run_gestor_falla_v9._normalizar_registro(raw, 1)
        self.assertEqual(normalized["nombre"], "Pau")
        self.assertEqual(normalized["concepto"], "cuota")
        self.assertEqual(normalized["importe_bruto"], 100)
        self.assertEqual(normalized["transaccion_id"], "TX-100")
        self.assertEqual(normalized["id_fallero"], "F-001")

    def test_cargar_registros_json_envuelto(self) -> None:
        self.input_json.write_text(
            json.dumps({"registros": [{"nombre": "Ana", "importe_bruto": 55, "concepto": "cuota"}]}),
            encoding="utf-8",
        )
        rows = run_gestor_falla_v9._cargar_registros(self.input_json)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["nombre"], "Ana")

    def test_main_procesa_y_guarda_salida(self) -> None:
        self.input_json.write_text(
            json.dumps(
                {
                    "registros": [
                        {
                            "nombre": "Pau",
                            "concepto": "cuota",
                            "importe_bruto": 100.0,
                            "transaccion_id": "TX-200",
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )

        argv = [
            "run_gestor_falla_v9.py",
            "--input",
            str(self.input_json),
            "--output",
            str(self.output_json),
            "--memory-path",
            str(self.mem_json),
        ]
        with patch("sys.argv", argv):
            rc = run_gestor_falla_v9.main()

        self.assertEqual(rc, 0)
        self.assertTrue(self.output_json.exists())
        payload = json.loads(self.output_json.read_text(encoding="utf-8"))
        self.assertEqual(len(payload["asientos"]), 1)
        self.assertEqual(payload["asientos"][0]["comision_aplicada"], 8.0)


if __name__ == "__main__":
    unittest.main()
