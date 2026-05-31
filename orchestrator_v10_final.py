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
"""


def _path() -> None:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))


def _run_py(script: str) -> int:
    r = subprocess.run([sys.executable, str(ROOT / script)], cwd=str(ROOT))
    return r.returncode


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

    args = p.parse_args()
    _path()

    if args.cmd == "produccion":
        from ejecutor_v10 import main as m

        return m()
    if args.cmd == "espejo":
        from unificar_v10 import ejecutar_secuencia_maestra

        return ejecutar_secuencia_maestra()
    if args.cmd == "bunker":
        from arranque_bunker_soberania import arranque_bunker

        return arranque_bunker()
    if args.cmd == "protocolo-despliegue":
        from protocolo_v10_despliegue import ejecutar_despliegue

        return ejecutar_despliegue()
    if args.cmd == "formalizar":
        from formalizar_soberania_v10 import formalizar_soberania

        formalizar_soberania()
        return 0
    if args.cmd == "monitor":
        import os
        from monitor_liquidacion_v10 import MonitorLiquidacion, _enviar_telegram

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
        from reporte_diario_soberania_v10 import main as m

        return m()
    if args.cmd == "bpifrance":
        from solicitud_liquidez_bpifrance_v10 import main as m

        return m()
    if args.cmd == "bpifrance-envio":
        from preparar_envio_bpifrance_v10 import preparar_envio_final

        preparar_envio_final()
        return 0
    if args.cmd == "bpifrance-token":
        from generar_secreto_bpifrance_v10 import generar_secreto_bpifrance

        generar_secreto_bpifrance()
        return 0
    if args.cmd == "rescate":
        from operacion_rescate_soberania_v10 import main as m

        return m()
    if args.cmd == "sellar-lafayette":
        from operacion_soberania_total_v10 import main as m

        return m()
    if args.cmd == "tesoreria":
        from gestion_tesoreria import main as m

        return m()
    if args.cmd == "metricas":
        from reporte_metricas_lafayette_v10 import reporte_metricas_lafayette

        reporte_metricas_lafayette()
        return 0
    if args.cmd == "divineo":
        return _run_py("motor_divineo_v10.py")
    if args.cmd == "vida":
        return _run_py("motor_vida_avatar_v10.py")
    if args.cmd == "certeza":
        return _run_py("motor_certeza_absoluta_v10.py")
    if args.cmd == "telegram-senal":
        from telegram_senal_soberania import enviar_senal_soberana

        return enviar_senal_soberana()
    if args.cmd == "gcs-contrato":
        from despliegue_gcs_soberano_v10 import subir_codice_v10

        return subir_codice_v10()
    if args.cmd == "gcs-core":
        from desplegar_v10_core_gcs import desplegar_configuracion

        return desplegar_configuracion()
    if args.cmd == "sacmuseum":
        from sacmuseum_empire import run_sacmuseum_sovereignty

        run_sacmuseum_sovereignty()
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
