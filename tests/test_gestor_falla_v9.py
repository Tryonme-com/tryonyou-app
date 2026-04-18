from __future__ import annotations

import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from gestor_falla_v9 import GestorFallaV9


class TestGestorFallaV9(unittest.TestCase):
    def test_procesa_cobro_valido_con_comision_y_neto(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            memory_path = Path(td) / "memoria.json"
            gestor = GestorFallaV9(memory_path=memory_path)
            result = gestor.ejecutar_cobro(
                {
                    "id_fallero": "F001",
                    "nombre": "Pau",
                    "concepto": "cuota",
                    "importe_bruto": 100.0,
                    "referencia_externa": "evt_1",
                }
            )

        self.assertEqual(result["status"], "ok")
        asiento = result["asiento"]
        self.assertEqual(asiento["importe_bruto_eur"], 100.0)
        self.assertEqual(asiento["comision_aplicada_eur"], 8.0)
        self.assertEqual(asiento["importe_neto_eur"], 92.0)
        self.assertEqual(asiento["estado"], "PAGADO")

    def test_marca_pendiente_regularizar_si_importe_es_bajo(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            memory_path = Path(td) / "memoria.json"
            gestor = GestorFallaV9(memory_path=memory_path)
            result = gestor.ejecutar_cobro(
                {
                    "id_fallero": "F010",
                    "nombre": "Lola",
                    "concepto": "cuota",
                    "importe_bruto": 35.0,
                    "referencia_externa": "evt_2",
                }
            )

        self.assertEqual(result["status"], "ok")
        asiento = result["asiento"]
        self.assertEqual(asiento["estado"], "Pendiente de regularizar")
        self.assertEqual(asiento["saldo_pendiente_eur"], 15.0)

    def test_detecta_duplicado_por_fingerprint(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            memory_path = Path(td) / "memoria.json"
            gestor = GestorFallaV9(memory_path=memory_path)
            registro = {
                "id_fallero": "F777",
                "nombre": "Nuria",
                "concepto": "evento",
                "importe_bruto": 70.0,
                "referencia_externa": "evt_dup",
            }
            first = gestor.ejecutar_cobro(registro)
            second = gestor.ejecutar_cobro(registro)

        self.assertEqual(first["status"], "ok")
        self.assertEqual(second["status"], "duplicado")
        self.assertEqual(second["referencia_externa"], "evt_dup")

    def test_detecta_duplicado_por_referencia_externa(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            memory_path = Path(td) / "memoria.json"
            gestor = GestorFallaV9(memory_path=memory_path)
            first = gestor.ejecutar_cobro(
                {
                    "id_fallero": "F700",
                    "nombre": "Ines",
                    "concepto": "evento",
                    "importe_bruto": 80.0,
                    "referencia_externa": "evt_ref_repetida",
                }
            )
            second = gestor.ejecutar_cobro(
                {
                    "id_fallero": "F701",
                    "nombre": "Ines 2",
                    "concepto": "evento",
                    "importe_bruto": 99.0,
                    "referencia_externa": "evt_ref_repetida",
                }
            )

        self.assertEqual(first["status"], "ok")
        self.assertEqual(second["status"], "duplicado")
        self.assertEqual(second["referencia_externa"], "evt_ref_repetida")

    def test_rechaza_concepto_invalido(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            memory_path = Path(td) / "memoria.json"
            gestor = GestorFallaV9(memory_path=memory_path)
            with self.assertRaises(ValueError):
                gestor.ejecutar_cobro(
                    {
                        "id_fallero": "F011",
                        "nombre": "Mia",
                        "concepto": "donacion",
                        "importe_bruto": 50.0,
                    }
                )

    def test_persistencia_de_memoria_entre_instancias(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            memory_path = Path(td) / "memoria.json"
            g1 = GestorFallaV9(memory_path=memory_path)
            g1.ejecutar_cobro(
                {
                    "id_fallero": "F100",
                    "nombre": "Pepe",
                    "concepto": "loteria",
                    "importe_bruto": 25.0,
                    "referencia_externa": "evt_x",
                }
            )
            g2 = GestorFallaV9(memory_path=memory_path)
            second = g2.ejecutar_cobro(
                {
                    "id_fallero": "F100",
                    "nombre": "Pepe",
                    "concepto": "loteria",
                    "importe_bruto": 25.0,
                    "referencia_externa": "evt_x",
                }
            )
            payload = json.loads(memory_path.read_text(encoding="utf-8"))

        self.assertEqual(second["status"], "duplicado")
        self.assertEqual(len(payload["asientos"]), 1)

    def test_lote_devuelve_resumen_procesados_y_duplicados(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            memory_path = Path(td) / "memoria.json"
            gestor = GestorFallaV9(
                comision_pct=Decimal("0.10"),
                cuota_base=Decimal("40.00"),
                memory_path=memory_path,
            )
            registros = [
                {
                    "id_fallero": "F001",
                    "nombre": "Ana",
                    "concepto": "cuota",
                    "importe_bruto": 50.0,
                    "referencia_externa": "evt_a",
                },
                {
                    "id_fallero": "F002",
                    "nombre": "Sergio",
                    "concepto": "evento",
                    "importe_bruto": 15.0,
                    "referencia_externa": "evt_b",
                },
                {
                    "id_fallero": "F001",
                    "nombre": "Ana",
                    "concepto": "cuota",
                    "importe_bruto": 50.0,
                    "referencia_externa": "evt_a",
                },
            ]
            result = gestor.procesar_lote(registros)

        self.assertEqual(result["total"], 3)
        self.assertEqual(result["procesados"], 2)
        self.assertEqual(result["duplicados"], 1)


if __name__ == "__main__":
    unittest.main()
