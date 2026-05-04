"""
Orquestador V10 final — un menú para los scripts del búnker (raíz del repo).

  python3 orchestrator_v10_final.py SUBCOMANDO

Ejemplos:
  python3 orchestrator_v10_final.py produccion
  python3 orchestrator_v10_final.py bunker
  python3 orchestrator_v10_final.py reporte-matutino
  python3 orchestrator_v10_final.py telegram-senal

Patente: PCT/EP2025/067317
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

_EPILOG = """
Subcomandos:
  produccion        ejecutor_v10 (cumplimiento + PDF + Telegram + Vite)
  espejo            unificar_v10 — mirror_ui + Gemini opcional
  bunker            arranque_bunker_soberania (Telegram + Vite + logo)
  protocolo-despliegue   protocolo_v10_despliegue (Telegram + Vite, sin Gemini)
  formalizar        formalizar_soberania_v10 (consola)
  monitor           monitor_liquidacion_v10 (+ Telegram si MONITOR_SEND_TELEGRAM=1)
  reporte-matutino  reporte_diario_soberania_v10 → centinela Telegram
  bpifrance         solicitud_liquidez_bpifrance_v10
  bpifrance-envio   preparar_envio_bpifrance_v10 (carpeta adjuntos)
  bpifrance-token   generar_secreto_bpifrance_v10
  rescate           operacion_rescate_soberania_v10
  sellar-lafayette  operacion_soberania_total_v10
  tesoreria         gestion_tesoreria (requiere TESORERIA_SALDO)
  metricas          reporte_metricas_lafayette_v10
  divineo           motor_divineo_v10 (subprocess)
  vida              motor_vida_avatar_v10 (subprocess)
  certeza           motor_certeza_absoluta_v10 (subprocess)
  telegram-senal    telegram_senal_soberania (plantilla TryOnYou)
  gcs-contrato      despliegue_gcs_soberano_v10
  gcs-core          desplegar_v10_core_gcs
  sacmuseum         sacmuseum_empire — soberanía económica (kill-switch + eventos)
  auditoria         auditoria_impacto_matinal — clearing bancario Lafayette/LVMH
  liquidez          auditoria_impacto_matinal --liquidez (monitor SEPA en tiempo real)
  reconciliar       auditoria_impacto_matinal --reconciliar-agresivo (retry invoices)
"""


def _path() -> None:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))


def _run_py(script: str) -> int:
    r = subprocess.run([sys.executable, str(ROOT / script)], cwd=str(ROOT))
    return r.returncode


def _missing_module(module: str) -> int:
    """Print a clear error when an optional module is not installed and return 1."""
    print(f"❌ Error: módulo '{module}' no encontrado. Ejecuta la instalación o inyección primero.")
    return 1


def main() -> int:
    p = argparse.ArgumentParser(
        description="TryOnYou V10 — orquestador final (menú de scripts).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=_EPILOG,
    )
    s = p.add_subparsers(dest="cmd", required=True)

    s.add_parser("produccion", help="ejecutor_v10: PDF + Telegram + Vite")
    s.add_parser("espejo", help="unificar_v10: mirror_ui + Gemini opcional")
    s.add_parser("bunker", help="arranque_bunker_soberania")
    s.add_parser(
        "protocolo-despliegue",
        help="protocolo_v10_despliegue: Telegram + Vite mirror_ui",
    )
    s.add_parser("formalizar", help="formalizar_soberania_v10")
    s.add_parser("monitor", help="monitor_liquidacion_v10")
    s.add_parser("reporte-matutino", help="reporte_diario_soberania_v10")
    s.add_parser("bpifrance", help="solicitud_liquidez_bpifrance_v10")
    s.add_parser("bpifrance-envio", help="preparar_envio_bpifrance_v10")
    s.add_parser("bpifrance-token", help="generar_secreto_bpifrance_v10")
    s.add_parser("rescate", help="operacion_rescate_soberania_v10")
    s.add_parser("sellar-lafayette", help="operacion_soberania_total_v10")
    s.add_parser("tesoreria", help="gestion_tesoreria")
    s.add_parser("metricas", help="reporte_metricas_lafayette_v10")
    s.add_parser("divineo", help="motor_divineo_v10")
    s.add_parser("vida", help="motor_vida_avatar_v10")
    s.add_parser("certeza", help="motor_certeza_absoluta_v10")
    s.add_parser("telegram-senal", help="telegram_senal_soberania")
    s.add_parser("gcs-contrato", help="despliegue_gcs_soberano_v10")
    s.add_parser("gcs-core", help="desplegar_v10_core_gcs")
    s.add_parser(
        "sacmuseum",
        help="sacmuseum_empire: kill-switch Lafayette, nodos CP, RelicValue, log fiestas",
    )
    s.add_parser(
        "auditoria",
        help="auditoria_impacto_matinal: clearing bancario Lafayette/LVMH",
    )
    s.add_parser(
        "liquidez",
        help="auditoria_impacto_matinal --liquidez: monitor SEPA en tiempo real",
    )
    s.add_parser(
        "reconciliar",
        help=(
            "auditoria_impacto_matinal --reconciliar-agresivo: "
            "retry inmediato invoices objetivo"
        ),
    )

    args = p.parse_args()
    _path()

    if args.cmd == "produccion":
        try:
            from ejecutor_v10 import main as m
        except ImportError:
            return _missing_module("ejecutor_v10")
        return m()
    if args.cmd == "espejo":
        try:
            from unificar_v10 import ejecutar_secuencia_maestra
        except ImportError:
            return _missing_module("unificar_v10")
        return ejecutar_secuencia_maestra()
    if args.cmd == "bunker":
        try:
            from arranque_bunker_soberania import arranque_bunker
        except ImportError:
            return _missing_module("arranque_bunker_soberania")
        return arranque_bunker()
    if args.cmd == "protocolo-despliegue":
        try:
            from protocolo_v10_despliegue import ejecutar_despliegue
        except ImportError:
            return _missing_module("protocolo_v10_despliegue")
        return ejecutar_despliegue()
    if args.cmd == "formalizar":
        try:
            from formalizar_soberania_v10 import formalizar_soberania
        except ImportError:
            return _missing_module("formalizar_soberania_v10")
        formalizar_soberania()
        return 0
    if args.cmd == "monitor":
        import os
        try:
            from monitor_liquidacion_v10 import MonitorLiquidacion, _enviar_telegram
        except ImportError:
            return _missing_module("monitor_liquidacion_v10")
        mon = MonitorLiquidacion()
        txt = mon.informe_diario()
        print(txt)
        if os.environ.get("MONITOR_SEND_TELEGRAM", "").strip() in (
            "1",
            "true",
            "yes",
        ):
            _enviar_telegram(txt)
        return 0
    if args.cmd == "reporte-matutino":
        try:
            from reporte_diario_soberania_v10 import main as m
        except ImportError:
            return _missing_module("reporte_diario_soberania_v10")
        return m()
    if args.cmd == "bpifrance":
        try:
            from solicitud_liquidez_bpifrance_v10 import main as m
        except ImportError:
            return _missing_module("solicitud_liquidez_bpifrance_v10")
        return m()
    if args.cmd == "bpifrance-envio":
        try:
            from preparar_envio_bpifrance_v10 import preparar_envio_final
        except ImportError:
            return _missing_module("preparar_envio_bpifrance_v10")
        preparar_envio_final()
        return 0
    if args.cmd == "bpifrance-token":
        try:
            from generar_secreto_bpifrance_v10 import generar_secreto_bpifrance
        except ImportError:
            return _missing_module("generar_secreto_bpifrance_v10")
        generar_secreto_bpifrance()
        return 0
    if args.cmd == "rescate":
        try:
            from operacion_rescate_soberania_v10 import main as m
        except ImportError:
            return _missing_module("operacion_rescate_soberania_v10")
        return m()
    if args.cmd == "sellar-lafayette":
        try:
            from operacion_soberania_total_v10 import main as m
        except ImportError:
            return _missing_module("operacion_soberania_total_v10")
        return m()
    if args.cmd == "tesoreria":
        try:
            from gestion_tesoreria import main as m
        except ImportError:
            return _missing_module("gestion_tesoreria")
        return m()
    if args.cmd == "metricas":
        try:
            from reporte_metricas_lafayette_v10 import reporte_metricas_lafayette
        except ImportError:
            return _missing_module("reporte_metricas_lafayette_v10")
        reporte_metricas_lafayette()
        return 0
    if args.cmd == "divineo":
        return _run_py("motor_divineo_v10.py")
    if args.cmd == "vida":
        return _run_py("motor_vida_avatar_v10.py")
    if args.cmd == "certeza":
        return _run_py("motor_certeza_absoluta_v10.py")
    if args.cmd == "telegram-senal":
        try:
            from telegram_senal_soberania import enviar_senal_soberana
        except ImportError:
            return _missing_module("telegram_senal_soberania")
        return enviar_senal_soberana()
    if args.cmd == "gcs-contrato":
        try:
            from despliegue_gcs_soberano_v10 import subir_codice_v10
        except ImportError:
            return _missing_module("despliegue_gcs_soberano_v10")
        return subir_codice_v10()
    if args.cmd == "gcs-core":
        try:
            from desplegar_v10_core_gcs import desplegar_configuracion
        except ImportError:
            return _missing_module("desplegar_v10_core_gcs")
        return desplegar_configuracion()
    if args.cmd == "sacmuseum":
        try:
            from sacmuseum_empire import run_sacmuseum_sovereignty
        except ImportError:
            return _missing_module("sacmuseum_empire")
        run_sacmuseum_sovereignty()
        return 0
    if args.cmd == "auditoria":
        try:
            from auditoria_impacto_matinal import main as m
        except ImportError:
            return _missing_module("auditoria_impacto_matinal")
        return m()
    if args.cmd == "liquidez":
        try:
            from auditoria_impacto_matinal import main as m
        except ImportError:
            return _missing_module("auditoria_impacto_matinal")
        return m(["--liquidez"])
    if args.cmd == "reconciliar":
        try:
            from auditoria_impacto_matinal import main as m
        except ImportError:
            return _missing_module("auditoria_impacto_matinal")
        return m(["--reconciliar-agresivo"])

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
