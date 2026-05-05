from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from gestor_falla_v9 import DuplicateCobroError, FallaCobroError, GestorFallaV9


class TestGestorFallaV9(unittest.TestCase):
    def test_procesa_cobro_y_registra_asiento_contable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            memory = Path(tmp) / "memorias.json"
            gestor = GestorFallaV9(memory_path=memory)

            asiento = gestor.ejecutar_cobro(
                "Pau",
                100,
                "Cuota Abril",
                id_fallero="f-001",
                fecha="05/05/2026",
                referencia_externa="pay_001",
            )

            self.assertEqual(asiento["fecha"], "2026-05-05")
            self.assertEqual(asiento["id_fallero"], "F-001")
            self.assertEqual(asiento["fallero"], "PAU")
            self.assertEqual(asiento["concepto_tipo"], "cuota")
            self.assertEqual(asiento["importe_bruto"], 100.0)
            self.assertEqual(asiento["comision_pct"], 0.08)
            self.assertEqual(asiento["comision_aplicada"], 8.0)
            self.assertEqual(asiento["neto_resultante"], 92.0)
            self.assertEqual(asiento["estado"], "PAGADO")

            data = json.loads(memory.read_text(encoding="utf-8"))
            self.assertEqual(data["falleros"]["F-001"]["saldo_pendiente"], 0.0)
            self.assertEqual(data["referencias_externas"], ["pay_001"])

    def test_marca_pendiente_regularizar_si_no_alcanza_cuota_minima(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            gestor = GestorFallaV9(memory_path=Path(tmp) / "memorias.json")

            asiento = gestor.ejecutar_cobro("Maria", 40, "Cuota Mayo", fecha="2026-05-05")

            self.assertEqual(asiento["estado"], "PENDIENTE_REGULARIZAR")
            self.assertEqual(asiento["saldo_pendiente"], 10.0)

    def test_cruza_deuda_existente_de_fallero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            memory = Path(tmp) / "memorias.json"
            memory.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "configuracion": {},
                        "falleros": {
                            "F-002": {
                                "nombre": "JOSE",
                                "saldo_pendiente": 120.0,
                            }
                        },
                        "asientos": [],
                        "fingerprints": [],
                        "referencias_externas": [],
                    }
                ),
                encoding="utf-8",
            )
            gestor = GestorFallaV9(memory_path=memory)

            asiento = gestor.ejecutar_cobro("Jose", 50, "Evento cena", id_fallero="F-002")

            self.assertEqual(asiento["estado"], "DEUDA_PENDIENTE")
            self.assertEqual(asiento["saldo_anterior"], 120.0)
            self.assertEqual(asiento["saldo_pendiente"], 70.0)

    def test_detecta_duplicado_por_referencia_externa(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            gestor = GestorFallaV9(memory_path=Path(tmp) / "memorias.json")
            record = {
                "nombre": "Paco",
                "importe_bruto": 50,
                "concepto": "Loteria Navidad",
                "referencia_externa": "stripe_evt_123",
            }

            gestor.procesar_registro(record)

            with self.assertRaises(DuplicateCobroError):
                gestor.procesar_registro({**record, "importe_bruto": 75})

    def test_detecta_duplicado_por_fingerprint_sin_referencia(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            gestor = GestorFallaV9(memory_path=Path(tmp) / "memorias.json")
            record = {
                "nombre": "Lola",
                "importe_bruto": 55,
                "concepto": "Cuota Junio",
                "fecha": "2026-06-01",
            }

            gestor.procesar_registro(record)

            with self.assertRaises(DuplicateCobroError):
                gestor.procesar_registro(record)

    def test_valida_concepto_permitido(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            gestor = GestorFallaV9(memory_path=Path(tmp) / "memorias.json")

            with self.assertRaises(FallaCobroError):
                gestor.ejecutar_cobro("Pau", 100, "Donativo externo")

    def test_acepta_aliases_de_payload_webhook(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            gestor = GestorFallaV9(memory_path=Path(tmp) / "memorias.json")

            asiento = gestor.procesar_registro(
                {
                    "fallero_nombre": "Ana Ferrer",
                    "monto": "80,00€",
                    "tipo": "Lotería",
                    "payment_id": "pay_alias",
                    "fecha": "05-05-2026",
                }
            )

            self.assertEqual(asiento["fallero"], "ANA FERRER")
            self.assertEqual(asiento["concepto_tipo"], "loteria")
            self.assertEqual(asiento["neto_resultante"], 73.6)

    def test_permuta_comision_y_cuota_por_constructor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            gestor = GestorFallaV9(
                comision_pct="0.05",
                cuota_base="60",
                memory_path=Path(tmp) / "memorias.json",
            )

            asiento = gestor.ejecutar_cobro("Vicent", 60, "Evento")

            self.assertEqual(asiento["comision_pct"], 0.05)
            self.assertEqual(asiento["comision_aplicada"], 3.0)
            self.assertEqual(asiento["neto_resultante"], 57.0)


if __name__ == "__main__":
    unittest.main()
