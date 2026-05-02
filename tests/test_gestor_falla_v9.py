from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from gestor_falla_v9 import (
    CobroDuplicadoError,
    GestorFallaV9,
    GestorFallaError,
)


class TestGestorFallaV9(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp(prefix="gestor_falla_v9_")
        self.memory_path = Path(self.tmp) / "memoria.json"

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _gestor(self, **kwargs: object) -> GestorFallaV9:
        return GestorFallaV9(memory_path=self.memory_path, **kwargs)

    def test_ejecutar_cobro_calcula_comision_y_neto(self) -> None:
        gestor = self._gestor(comision_pct=0.08, cuota_base=50)

        asiento = gestor.ejecutar_cobro(
            id_fallero="F-001",
            nombre="Pau",
            bruto=100,
            concepto="cuota",
            fecha=date(2026, 5, 2),
            referencia_externa="stripe_evt_001",
        )

        self.assertEqual(asiento["fallero"], "PAU")
        self.assertEqual(asiento["importe_bruto"], "100.00 EUR")
        self.assertEqual(asiento["comision_aplicada"], "8.00 EUR")
        self.assertEqual(asiento["neto_resultante"], "92.00 EUR")
        self.assertEqual(asiento["estado"], "PAGADO")
        self.assertEqual(asiento["fecha"], "2026-05-02")
        self.assertEqual(asiento["referencia_externa"], "stripe_evt_001")

    def test_marca_pendiente_si_cobro_es_menor_a_cuota_minima(self) -> None:
        gestor = self._gestor(comision_pct=0.08, cuota_base=50)

        asiento = gestor.ejecutar_cobro(
            id_fallero="F-002",
            nombre="Marta",
            bruto=30,
            concepto="cuota",
            fecha="2026-05-02",
        )

        self.assertEqual(asiento["estado"], "Pendiente de regularizar")
        self.assertEqual(asiento["saldo_pendiente"], "20.00 EUR")

    def test_actualiza_saldo_pendiente_en_memoria(self) -> None:
        gestor = self._gestor(comision_pct=0.08, cuota_base=50)

        gestor.ejecutar_cobro(
            id_fallero="F-003",
            nombre="Ruben",
            bruto=20,
            concepto="cuota",
            fecha="2026-05-02",
        )
        gestor.ejecutar_cobro(
            id_fallero="F-003",
            nombre="Ruben",
            bruto=35,
            concepto="cuota",
            fecha="2026-05-03",
        )

        memoria = json.loads(self.memory_path.read_text(encoding="utf-8"))
        self.assertEqual(memoria["falleros"]["F-003"]["saldo_pendiente"], "45.00")
        self.assertEqual(len(memoria["falleros"]["F-003"]["transacciones"]), 2)

    def test_persiste_y_recupera_historico(self) -> None:
        gestor = self._gestor()
        gestor.ejecutar_cobro(
            id_fallero="F-004",
            nombre="Laura",
            bruto=50,
            concepto="evento",
            fecha="2026-05-02",
        )

        memoria = json.loads(self.memory_path.read_text(encoding="utf-8"))
        self.assertEqual(len(memoria["transacciones"]), 1)
        self.assertEqual(memoria["transacciones"][0]["id_fallero"], "F-004")

    def test_bloquea_duplicados_por_referencia_externa(self) -> None:
        gestor = self._gestor()
        kwargs = {
            "id_fallero": "F-005",
            "nombre": "Nuria",
            "bruto": 50,
            "concepto": "loteria",
            "fecha": "2026-05-02",
            "referencia_externa": "make_webhook_001",
        }

        gestor.ejecutar_cobro(**kwargs)

        with self.assertRaises(CobroDuplicadoError):
            gestor.ejecutar_cobro(**kwargs)

    def test_valida_concepto_permitido(self) -> None:
        gestor = self._gestor()

        with self.assertRaises(GestorFallaError):
            gestor.ejecutar_cobro(
                id_fallero="F-006",
                nombre="Vicent",
                bruto=50,
                concepto="camiseta",
                fecha="2026-05-02",
            )

    def test_rechaza_importe_no_positivo(self) -> None:
        gestor = self._gestor()

        with self.assertRaises(GestorFallaError):
            gestor.ejecutar_cobro(
                id_fallero="F-007",
                nombre="Ana",
                bruto=0,
                concepto="cuota",
                fecha="2026-05-02",
            )

    def test_configuracion_desde_entorno(self) -> None:
        old = {
            "FALLA_COMISION_PCT": os.environ.get("FALLA_COMISION_PCT"),
            "FALLA_CUOTA_BASE": os.environ.get("FALLA_CUOTA_BASE"),
        }
        os.environ["FALLA_COMISION_PCT"] = "0.1"
        os.environ["FALLA_CUOTA_BASE"] = "60"
        try:
            gestor = GestorFallaV9(memory_path=self.memory_path)
            asiento = gestor.ejecutar_cobro(
                id_fallero="F-008",
                nombre="Pau",
                bruto=100,
                concepto="cuota",
                fecha="2026-05-02",
            )
        finally:
            for key, value in old.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

        self.assertEqual(asiento["comision_aplicada"], "10.00 EUR")
        self.assertEqual(asiento["comision_pct"], "0.10")


if __name__ == "__main__":
    unittest.main()
