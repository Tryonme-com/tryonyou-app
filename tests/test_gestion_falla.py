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

from logic.gestion_falla import ESTADO_PAGADO, ESTADO_PENDIENTE, GestorFallaV9


class TestGestorFallaV9(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        base = Path(self.temp_dir.name)
        self.memory = base / "data" / "memories.json"
        self.ledger = base / "logs" / "cobros.jsonl"
        self.gestor = GestorFallaV9(
            memoria_path=self.memory,
            libro_path=self.ledger,
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_calcula_comision_neto_y_asiento_al_ocho_por_ciento(self) -> None:
        asiento = self.gestor.ejecutar_cobro(
            "Pau",
            100,
            "Cuota Abril",
            referencia="pay_001",
            fallero_id="F-001",
            fecha="2026-04-10",
        )

        self.assertEqual(asiento["fecha"], "2026-04-10")
        self.assertEqual(asiento["fallero_id"], "F-001")
        self.assertEqual(asiento["fallero"], "PAU")
        self.assertEqual(asiento["importe_bruto"], 100.0)
        self.assertEqual(asiento["comision_pct"], 0.08)
        self.assertEqual(asiento["comision_aplicada"], 8.0)
        self.assertEqual(asiento["neto_resultante"], 92.0)
        self.assertEqual(asiento["saldo_pendiente"], 0.0)
        self.assertEqual(asiento["estado"], ESTADO_PAGADO)
        self.assertFalse(asiento["duplicado"])

    def test_marca_cobro_inferior_y_actualiza_saldo_pendiente(self) -> None:
        asiento = self.gestor.ejecutar_cobro(
            "Maria M.",
            "40.00",
            "Cuota Anual",
            referencia="pay_bajo",
            fecha="2026-07-17",
        )

        self.assertEqual(asiento["estado"], ESTADO_PENDIENTE)
        self.assertEqual(asiento["saldo_pendiente"], 10.0)
        self.assertEqual(asiento["comision_aplicada"], 3.2)
        self.assertEqual(asiento["neto_resultante"], 36.8)

    def test_conserva_precision_de_una_comision_personalizada(self) -> None:
        gestor = GestorFallaV9(
            comision_pct="0.075",
            memoria_path=self.memory,
            libro_path=self.ledger,
        )

        asiento = gestor.ejecutar_cobro(
            "Pau",
            100,
            "Evento Presentación",
            referencia="fee_075",
        )

        self.assertEqual(asiento["comision_pct"], 0.075)
        self.assertEqual(asiento["comision_aplicada"], 7.5)
        self.assertEqual(asiento["neto_resultante"], 92.5)

    def test_reintento_no_duplica_memoria_ni_libro(self) -> None:
        first = self.gestor.ejecutar_cobro(
            "José S.",
            200,
            "Lotería",
            referencia="stripe_pi_123",
            fecha="2026-07-17",
        )
        second = self.gestor.ejecutar_cobro(
            "José S.",
            200,
            "Lotería",
            referencia="stripe_pi_123",
            fecha="2026-07-17",
        )

        self.assertFalse(first["duplicado"])
        self.assertTrue(second["duplicado"])
        self.assertEqual(len(self.gestor.obtener_resumen()), 1)
        ledger_lines = self.ledger.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(ledger_lines), 1)
        self.assertEqual(json.loads(ledger_lines[0])["referencia"], "stripe_pi_123")

    def test_persistencia_sobrevive_a_una_nueva_instancia(self) -> None:
        self.gestor.ejecutar_cobro(
            "Pau",
            100,
            "Evento Presentación",
            referencia="evt_001",
        )
        reloaded = GestorFallaV9(
            memoria_path=self.memory,
            libro_path=self.ledger,
        )

        self.assertEqual(len(reloaded.obtener_resumen()), 1)
        self.assertEqual(reloaded.obtener_resumen()[0]["referencia"], "evt_001")

    def test_payload_make_admite_aliases_estables(self) -> None:
        resultados = self.gestor.procesar_registros(
            [
                {
                    "nombre": "Paco G.",
                    "monto": 75,
                    "tipo": "Cuota Mayo",
                    "payment_id": "make_001",
                    "fallero_id": "F-075",
                    "fecha": "2026-05-01",
                }
            ]
        )

        self.assertEqual(resultados[0]["referencia"], "make_001")
        self.assertEqual(resultados[0]["fallero_id"], "F-075")
        self.assertEqual(resultados[0]["neto_resultante"], 69.0)

    def test_referencia_automatica_es_idempotente(self) -> None:
        first = self.gestor.ejecutar_cobro(
            "Ana Pérez",
            50,
            "Cuota Junio",
            fecha="2026-06-01",
        )
        second = self.gestor.ejecutar_cobro(
            " Ana   Pérez ",
            "50.0",
            "cuota junio",
            fecha="2026-06-01",
        )

        self.assertEqual(first["referencia"], second["referencia"])
        self.assertTrue(second["duplicado"])

    def test_rechaza_datos_financieros_invalidos(self) -> None:
        casos = [
            ("", 50, "Cuota"),
            ("Pau", 0, "Cuota"),
            ("Pau", -1, "Cuota"),
            ("Pau", True, "Cuota"),
            ("Pau", 50, "Donativo"),
        ]
        for nombre, bruto, concepto in casos:
            with self.subTest(nombre=nombre, bruto=bruto, concepto=concepto):
                with self.assertRaises(ValueError):
                    self.gestor.ejecutar_cobro(nombre, bruto, concepto)

    def test_rechaza_reutilizar_id_para_otro_fallero(self) -> None:
        self.gestor.ejecutar_cobro(
            "Pau",
            50,
            "Cuota Abril",
            fallero_id="F-001",
            referencia="pay_001",
        )

        with self.assertRaisesRegex(ValueError, "pertenece a otro nombre"):
            self.gestor.ejecutar_cobro(
                "María",
                50,
                "Cuota Abril",
                fallero_id="F-001",
                referencia="pay_002",
            )


if __name__ == "__main__":
    unittest.main()
