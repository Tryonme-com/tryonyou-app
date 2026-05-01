import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

import sys

_ROOT = str(Path(__file__).resolve().parents[1])
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from gestor_falla_v9 import (  # noqa: E402
    DuplicateCobroError,
    GestorFallaError,
    GestorFallaV9,
    _pct,
)


class TestGestorFallaV9(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.memory = Path(self.tmp.name) / "falla_memorias.json"

    def tearDown(self):
        self.tmp.cleanup()

    def test_ejecutar_cobro_calcula_comision_y_neto(self):
        gestor = GestorFallaV9(comision_pct=0.08, cuota_base=50, memory_path=self.memory)

        asiento = gestor.ejecutar_cobro(
            "Pau",
            100,
            "cuota",
            id_fallero="FALLA-001",
            referencia_externa="stripe_pi_1",
            fecha="2026-05-01",
        )

        self.assertEqual(asiento["fecha"], "2026-05-01")
        self.assertEqual(asiento["id_fallero"], "FALLA-001")
        self.assertEqual(asiento["fallero"], "PAU")
        self.assertEqual(asiento["importe_bruto"], 100.0)
        self.assertEqual(asiento["comision_aplicada"], 8.0)
        self.assertEqual(asiento["neto_resultante"], 92.0)
        self.assertEqual(asiento["saldo_pendiente"], 0.0)
        self.assertEqual(asiento["estado"], "PAGADO")

    def test_cuota_inferior_genera_pendiente_regularizar_y_deuda(self):
        gestor = GestorFallaV9(comision_pct=0.08, cuota_base=50, memory_path=self.memory)

        asiento = gestor.ejecutar_cobro(
            "Maria",
            "40,00",
            "cuota",
            id_fallero="FALLA-002",
            referencia_externa="stripe_pi_2",
            fecha="2026-05-01",
        )

        self.assertEqual(asiento["estado"], "Pendiente de regularizar")
        self.assertEqual(asiento["saldo_pendiente"], 10.0)

        data = json.loads(self.memory.read_text(encoding="utf-8"))
        self.assertEqual(data["falleros"]["FALLA-002"]["saldo_pendiente"], 10.0)

    def test_pago_posterior_reduce_deuda_de_cuota(self):
        gestor = GestorFallaV9(comision_pct=0.08, cuota_base=50, memory_path=self.memory)

        gestor.ejecutar_cobro(
            "Maria",
            40,
            "cuota",
            id_fallero="FALLA-002",
            referencia_externa="stripe_pi_2",
            fecha="2026-05-01",
        )
        regularizacion = gestor.ejecutar_cobro(
            "Maria",
            60,
            "cuota",
            id_fallero="FALLA-002",
            referencia_externa="stripe_pi_3",
            fecha="2026-05-02",
        )

        self.assertEqual(regularizacion["saldo_pendiente"], 0.0)

    def test_loteria_no_modifica_deuda_de_cuota(self):
        gestor = GestorFallaV9(comision_pct=0.08, cuota_base=50, memory_path=self.memory)

        gestor.ejecutar_cobro(
            "Jose",
            35,
            "cuota",
            id_fallero="FALLA-003",
            referencia_externa="stripe_pi_4",
            fecha="2026-05-01",
        )
        loteria = gestor.ejecutar_cobro(
            "Jose",
            200,
            "lotería",
            id_fallero="FALLA-003",
            referencia_externa="stripe_pi_5",
            fecha="2026-05-02",
        )

        self.assertEqual(loteria["concepto"], "loteria")
        self.assertEqual(loteria["saldo_pendiente"], 15.0)

    def test_rechaza_duplicado_por_referencia(self):
        gestor = GestorFallaV9(comision_pct=0.08, cuota_base=50, memory_path=self.memory)
        kwargs = {
            "nombre": "Pau",
            "bruto": 100,
            "concepto": "cuota",
            "id_fallero": "FALLA-001",
            "referencia_externa": "stripe_pi_dup",
            "fecha": "2026-05-01",
        }

        gestor.ejecutar_cobro(**kwargs)

        with self.assertRaises(DuplicateCobroError):
            gestor.ejecutar_cobro(**kwargs)

    def test_procesar_lote_separa_aceptados_duplicados_y_errores(self):
        gestor = GestorFallaV9(comision_pct=0.08, cuota_base=50, memory_path=self.memory)

        result = gestor.procesar_lote(
            [
                {
                    "id_fallero": "FALLA-001",
                    "nombre": "Pau",
                    "monto": 100,
                    "tipo": "cuota",
                    "referencia_externa": "ref-ok",
                    "fecha": "2026-05-01",
                },
                {
                    "id_fallero": "FALLA-001",
                    "nombre": "Pau",
                    "monto": 100,
                    "tipo": "cuota",
                    "referencia_externa": "ref-ok",
                    "fecha": "2026-05-01",
                },
                {
                    "id_fallero": "FALLA-002",
                    "nombre": "A",
                    "monto": 10,
                    "tipo": "donativo",
                },
            ]
        )

        self.assertEqual(len(result["accepted"]), 1)
        self.assertEqual(len(result["duplicates"]), 1)
        self.assertEqual(len(result["errors"]), 1)

    def test_valida_concepto_fecha_y_porcentaje(self):
        with self.assertRaises(GestorFallaError):
            GestorFallaV9(comision_pct=0.08, cuota_base=50, memory_path=self.memory).ejecutar_cobro(
                "Pau",
                100,
                "donativo",
                fecha="2026-05-01",
            )

        with self.assertRaises(GestorFallaError):
            GestorFallaV9(comision_pct=0.08, cuota_base=50, memory_path=self.memory).ejecutar_cobro(
                "Pau",
                100,
                "cuota",
                fecha="01/05/2026",
            )

        self.assertEqual(_pct("7.5"), Decimal("0.0750"))


if __name__ == "__main__":
    unittest.main()
