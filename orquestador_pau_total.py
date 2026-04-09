"""
Orquestación total TryOnYou / Agente @Pau — un solo punto de entrada.

Ejecutar desde la raíz del proyecto (donde está el CSV de leads, si aplica):

    python3 orquestador_pau_total.py

Variables de entorno (opcionales):

    ORQUESTA_MODE       total | ligero | entrega_only | github_only  (default: total)
    ORQUESTA_ENTREGA    omega | paloma | divineo | jules            (default: omega)
    ORQUESTA_SKIP_ENTREGA  1  — no genera carpetas en el Escritorio ni purga de entrega
    ORQUESTA_GITHUB_PR  0 | 2264 | 2266  — merge vía API si GITHUB_TOKEN está definido
    ORQUESTA_PURGA_GITHUB  1  — antes del merge 2266, ejecuta también purgar_friccion (v10_terminal)
    ORQUESTA_SLACK_TEST   — ref. destino para disparo Jules vía Slack (requiere SLACK_WEBHOOK_URL)
    ORQUESTA_EMAIL_TEST   — alias heredado; mismo efecto que ORQUESTA_SLACK_TEST

Fases en modo *total* (por defecto):
  1) Protocolo liquidez / estado búnker
  2) Validación cola email + log en Escritorio
  3) Entrega maestra en Escritorio (una sola variante para no duplicar purgas)
  4) GitHub (solo si ORQUESTA_GITHUB_PR != 0)
  5) Jules / Slack de prueba (solo si ORQUESTA_SLACK_TEST u ORQUESTA_EMAIL_TEST = ref. destino)
  6) Registro simbólico monetario

La vigilancia en bucle infinito no se arranca aquí; sigue siendo: python3 vigilancia_pau.py
"""

from __future__ import annotations

import os
import sys
import traceback
from typing import Callable


def _banner(titulo: str) -> None:
    print(f"\n{'═' * 58}\n  {titulo}\n{'═' * 58}")


def _fase(nombre: str, fn: Callable[[], None], continuar_si_falla: bool = True) -> bool:
    """
    Ejecuta una fase.

    - continuar_si_falla=True (default): ante error, mensaje breve sin traceback; el orquestador puede seguir.
    - continuar_si_falla=False: ante error, mensaje + traceback completo; el llamador suele hacer sys.exit(1).
    """
    _banner(nombre)
    try:
        fn()
        return True
    except Exception as e:
        print(f"⚠️  Fase «{nombre}»: {e}")
        if not continuar_si_falla:
            traceback.print_exc()
        return False


def _fase_protocolo() -> None:
    from protocolo_liquidez_stealth import protocolo_liquidez_stealth

    estado = protocolo_liquidez_stealth()
    print(f"📋 Estado: {estado}")


def _fase_jules_validator() -> None:
    from jules_email_validator import Jules_Email_Validator

    Jules_Email_Validator().validar_y_registrar()


def _fase_entrega() -> None:
    entrega = os.getenv("ORQUESTA_ENTREGA", "omega").strip().lower()
    handlers: dict[str, Callable[[], None]] = {
        "omega": _run_mirror_omega,
        "paloma": _run_mirror_paloma,
        "divineo": _run_divineo,
        "jules": _run_jules_monetizador,
    }
    if entrega not in handlers:
        print(f"❌ ORQUESTA_ENTREGA desconocida: {entrega!r}. Usa: {', '.join(handlers)}")
        return
    handlers[entrega]()


def _run_mirror_omega() -> None:
    from mirror_sanctuary_orchestrator_v10_omega import MirrorSanctuaryOrchestrator_V10_Omega

    MirrorSanctuaryOrchestrator_V10_Omega().ejecutar_mision_paloma()


def _run_mirror_paloma() -> None:
    from mirror_sanctuary_orchestrator import MirrorSanctuaryOrchestrator

    MirrorSanctuaryOrchestrator().ejecutar_mision_paloma()


def _run_divineo() -> None:
    from deploy_divineo import deploy_divineo

    deploy_divineo()


def _run_jules_monetizador() -> None:
    from agente_jules_monetizador_v10 import AgenteJules_Monetizador_V10

    AgenteJules_Monetizador_V10().ejecutar_mision_directa()


def _fase_github() -> None:
    pr = os.getenv("ORQUESTA_GITHUB_PR", "0").strip()
    if pr in ("", "0", "no", "false"):
        print("ℹ️  ORQUESTA_GITHUB_PR=0 — sin merge GitHub en esta corrida.")
        return
    if pr == "2264":
        from agente_ejecutor_pr2264 import agente_ejecutor_pr2264

        agente_ejecutor_pr2264()
        return
    if pr == "2266":
        from v10_terminal import AgenteBunkerPR2266

        agente = AgenteBunkerPR2266()
        if os.getenv("ORQUESTA_PURGA_GITHUB", "").strip() in ("1", "true", "yes", "on"):
            agente.purgar_friccion()
        agente.sellar_pr()
        return
    print(f"⚠️  ORQUESTA_GITHUB_PR={pr!r} no reconocido (usa 2264 o 2266).")


def _fase_email_opcional() -> None:
    dest = (
        os.getenv("ORQUESTA_SLACK_TEST", "").strip()
        or os.getenv("ORQUESTA_EMAIL_TEST", "").strip()
    )
    if not dest:
        print(
            "ℹ️  Sin ORQUESTA_SLACK_TEST ni ORQUESTA_EMAIL_TEST — sin disparo Jules (Slack)."
        )
        return
    from jules_force_execution import JulesForceExecution

    JulesForceExecution().disparar_prueba_real(dest)


def _fase_registro() -> None:
    from registrar_exito_monetario import registrar_exito_monetario

    registrar_exito_monetario("ORQUESTA_TOTAL_DIVINEO")


def orquestar() -> None:
    mode = os.getenv("ORQUESTA_MODE", "total").strip().lower()
    skip_entrega = os.getenv("ORQUESTA_SKIP_ENTREGA", "").strip() in ("1", "true", "yes", "on")

    print(
        "\n🦚 Orquestador @Pau — modo "
        f"{mode!r} | entrega={os.getenv('ORQUESTA_ENTREGA', 'omega')!r} "
        f"| skip_entrega={skip_entrega}"
    )

    if mode == "github_only":
        if not _fase("GitHub API", _fase_github, continuar_si_falla=False):
            sys.exit(1)
        return

    if mode == "entrega_only":
        if not _fase("Entrega Escritorio", _fase_entrega, continuar_si_falla=False):
            sys.exit(1)
        return

    if mode == "ligero":
        _fase("Protocolo liquidez", _fase_protocolo)
        _fase("Jules — validación / log", _fase_jules_validator)
        _fase("Registro monetario", _fase_registro)
        _banner("Fin modo ligero")
        return

    if mode != "total":
        print(f"⚠️  ORQUESTA_MODE={mode!r} no reconocido; uso «total».")
        mode = "total"

    _fase("Protocolo liquidez", _fase_protocolo)
    _fase("Jules — validación / log", _fase_jules_validator)
    if not skip_entrega:
        _fase("Entrega maestra (Escritorio)", _fase_entrega)
    else:
        print("\n⏭️  ORQUESTA_SKIP_ENTREGA=1 — fase de carpetas en Escritorio omitida.")

    _fase("GitHub (opcional)", _fase_github)
    _fase("Jules Slack prueba (opcional)", _fase_email_opcional)
    _fase("Registro monetario", _fase_registro)
    _banner("Orquestación total completada (revisa avisos arriba si hubo fallos parciales)")


if __name__ == "__main__":
    try:
        orquestar()
    except KeyboardInterrupt:
        print("\n🛑 Orquestador detenido por el usuario.")
        sys.exit(130)
