"""
Cerebro del Búnker — orquestador de validación y despliegue (PAU / TryOnYou).

- Por defecto ejecuta el pipeline completo vía ``scripts/deployall.sh`` (tests, tsc, build, Vercel).
- Modo rápido: solo ``vercel_deploy_orchestrator.deploy_sovereign_network`` (requiere ``VERCEL_TOKEN``).

Variables de entorno:
  VERCEL_TOKEN — obligatorio para despliegue real (no volcar en chat).
  ORCHESTRATOR_REQUIRE_STRIPE=1 — exige ``STRIPE_SECRET_KEY`` antes de desplegar.

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""

from __future__ import annotations

import argparse
import logging
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEPLOYALL = ROOT / "scripts" / "deployall.sh"

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger("Bunker_Orchestrator")


class DeploymentAgent:
    """Agente PAU: valida entorno y lanza el despliegue acordado al proyecto."""

    def __init__(self) -> None:
        self.deployment_tool = "vercel"

    def validate_environment(self, *, require_stripe: bool) -> bool:
        """Comprueba requisitos mínimos antes de subir a producción."""
        logger.info("Agente PAU: validando integridad de entorno...")
        if require_stripe and not os.environ.get("STRIPE_SECRET_KEY", "").strip():
            logger.error("PAU: STRIPE_SECRET_KEY ausente (ORCHESTRATOR_REQUIRE_STRIPE=1).")
            return False
        return True

    def run_full_pipeline(self) -> int:
        """Build + tests + Vercel (mismo criterio que CI local)."""
        if not DEPLOYALL.is_file():
            logger.error("No se encuentra %s", DEPLOYALL)
            return 1
        logger.info("PAU: ejecutando pipeline completo (deployall.sh)...")
        proc = subprocess.run(
            ["bash", str(DEPLOYALL)],
            cwd=ROOT,
        )
        return int(proc.returncode)

    def run_full_pipeline_dry(self) -> int:
        """Solo validación y build; sin ``vercel --prod``."""
        if not DEPLOYALL.is_file():
            logger.error("No se encuentra %s", DEPLOYALL)
            return 1
        logger.info("PAU: dry-run — build y tests, sin despliegue.")
        proc = subprocess.run(
            ["bash", str(DEPLOYALL), "--dry"],
            cwd=ROOT,
        )
        return int(proc.returncode)

    def deploy_vercel_only(self) -> int:
        """Solo despliegue Vercel + actualización de manifiesto (sin redeployall)."""
        logger.info("PAU: modo --vercel-only (vercel_deploy_orchestrator).")
        try:
            from vercel_deploy_orchestrator import deploy_sovereign_network
        except ImportError as e:
            logger.error("No se pudo importar vercel_deploy_orchestrator: %s", e)
            return 1
        return deploy_sovereign_network()


def run_autonomous_mission(
    *,
    dry_run: bool,
    vercel_only: bool,
    require_stripe: bool,
) -> int:
    pau = DeploymentAgent()
    if not pau.validate_environment(require_stripe=require_stripe):
        logger.error("PAU: entorno incompleto. Operación abortada.")
        return 1

    if dry_run and vercel_only:
        logger.error("Combina --dry-run con pipeline completo o usa solo --dry-run.")
        return 1

    if dry_run:
        logger.info("PAU: entorno validado. Ejecutando dry-run.")
        return pau.run_full_pipeline_dry()

    if vercel_only:
        logger.info("PAU: entorno validado. Despliegue Vercel directo.")
        if not os.environ.get("VERCEL_TOKEN", "").strip():
            logger.error("PAU: define VERCEL_TOKEN para despliegue.")
            return 1
        return pau.deploy_vercel_only()

    logger.info("PAU: entorno validado. Pipeline completo → producción.")
    return pau.run_full_pipeline()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Orquestador Búnker — validación y despliegue TryOnYou (Vercel).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Tests + build sin desplegar (equivalente a deployall.sh --dry).",
    )
    parser.add_argument(
        "--vercel-only",
        action="store_true",
        help="Solo vercel_deploy_orchestrator (sin npm test/build previo en este script).",
    )
    args = parser.parse_args(argv)

    require_stripe = os.environ.get("ORCHESTRATOR_REQUIRE_STRIPE", "").strip() == "1"
    code = run_autonomous_mission(
        dry_run=args.dry_run,
        vercel_only=args.vercel_only,
        require_stripe=require_stripe,
    )
    if code == 0:
        logger.info("Misión completada.")
    else:
        logger.warning("Misión terminada con código %s.", code)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
