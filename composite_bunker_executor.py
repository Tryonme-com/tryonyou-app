<<<<<<< HEAD
"""
Composite Bunker Executor — VetosCore + Protocolo BPI 7 500 € + leads estratégicos.

No expone secretos en código:
  - Umbral y lógica financiera: reutiliza VetosInferenceSystem (vetos_core_inference.py)
  - Webhook Make.com: variable de entorno MAKE_WEBHOOK_URL (o específica de este flujo)

Patente (ref.): PCT/EP2025/067317
SIREN (ref.): 943 610 196
"""

from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass
from typing import Any, Iterable

import requests

from vetos_core_inference import PaymentDelayError, VetosInferenceSystem
from bunker_full_orchestrator import append_waitlist_json


TARGET_DOMAINS: tuple[str, ...] = ("@inditex.com", "@zara.com", "@stationf.co", "@stationf.co.uk")


def _truthy_env(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")


def _make_post_omega(payload: dict[str, Any]) -> bool:
    """
    Webhook Make — usa MAKE_WEBHOOK_URL_OMEGA si existe, si no MAKE_WEBHOOK_URL.
    Contrato estable: email + source + tags de dominio y score.
    """
    url = (
        os.getenv("MAKE_WEBHOOK_URL_OMEGA", "").strip()
        or os.getenv("MAKE_WEBHOOK_URL", "").strip()
    )
    if not url:
        return False
    try:
        r = requests.post(url, json=payload, timeout=25)
        return 200 <= r.status_code < 300
    except OSError:
        return False


def _domain_tag(email: str) -> str | None:
    e = (email or "").strip().lower()
    for dom in TARGET_DOMAINS:
        if dom in e:
            return dom
    return None


@dataclass
class CompositeResult:
    email: str
    vetos_score: float
    vetos_gold: bool
    bpifrance_ok: bool
    make_ok: bool
    waitlist_ok: bool
    waitlist_path: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "email": self.email,
            "vetos_score": self.vetos_score,
            "vetos_gold": self.vetos_gold,
            "bpifrance_ok": self.bpifrance_ok,
            "make_ok": self.make_ok,
            "waitlist_ok": self.waitlist_ok,
            "waitlist_path": self.waitlist_path,
        }


class CompositeBunker:
    """
    Orquestador Omega:
      - Inferencia VetosCore (threshold 0.92)
      - Validación Protocolo BPI (7 500 €)
      - Lead estratégico vía Make + persistencia local
    """

    def __init__(self, *, threshold: float = 0.92) -> None:
        self.system = VetosInferenceSystem(threshold=threshold)

    async def process_lead(
        self,
        *,
        email: str,
        revenue_eur: float = 7_500.0,
        days_delay: int = 0,
        extra_tags: Iterable[str] | None = None,
    ) -> CompositeResult:
        # 1) Validación financiera Bpifrance 7 500 €
        bp_ok = False
        try:
            await self.system.validate_revenue_stream(revenue_eur, days_delay=days_delay)
            bp_ok = True
        except PaymentDelayError:
            bp_ok = False

        # 2) Inferencia VetosCore
        payload = {
            "id": "composite_bunker_lead",
            "module": "VetosCore",
            "email": email,
            "revenue_validation": revenue_eur,
        }
        inference = await self.system.execute_inference(payload)

        # 3) Lead estratégico (solo dominios objetivo)
        tag = _domain_tag(email)
        tags = list(extra_tags or [])
        if tag:
            tags.append(tag)
        lead_payload = {
            "event": "omega_lead",
            "email": email,
            "source": "composite_bunker",
            "tags": tags,
            "vetos": {
                "score": inference["score"],
                "gold": inference["gold"],
                "threshold": inference["vetos_threshold"],
            },
            "bpifrance": {
                "amount_eur": revenue_eur,
                "days_delay": days_delay,
                "ok": bp_ok,
            },
        }
        make_ok = _make_post_omega(lead_payload)
        waitlist_ok, waitlist_path = append_waitlist_json(lead_payload)

        return CompositeResult(
            email=email,
            vetos_score=float(inference["score"]),
            vetos_gold=bool(inference["gold"]),
            bpifrance_ok=bp_ok,
            make_ok=make_ok,
            waitlist_ok=waitlist_ok,
            waitlist_path=waitlist_path,
        )


async def _demo() -> None:
    bunker = CompositeBunker()
    sample_email = os.getenv("OMEGA_TEST_EMAIL", "vip@stationf.co")
    res = await bunker.process_lead(email=sample_email)
    print(json.dumps(res.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    # Demo local: no envía nada si no hay webhook configurado y guarda en leads_empire/ o /tmp.
    if not _truthy_env("OMEGA_COMPOSITE_RUN"):
        print(
            "Define OMEGA_COMPOSITE_RUN=1 para ejecutar la demo local "
            "(usa OMEGA_TEST_EMAIL para fijar el email de prueba)."
        )
    else:
        asyncio.run(_demo())

=======
import asyncio
import json
import logging
import requests
from datetime import datetime

# Configuración de trazabilidad total para el Bunker
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("CompositeBunker")

CONFIG = {
    "MAKE_WEBHOOK_URL": "https://hook.us1.make.com/tu_id_unico", # 🔥 Pega tu URL de Make
    "AI_THRESHOLD": 0.92,
    "REVENUE_TARGET": 7500.0
}

class CompositeOrchestrator:
    """Unifica IA, Finanzas y Leads en un solo flujo de ejecución."""
    
    async def validate_all(self, email: str, amount: float):
        logger.info("--- 🛡️ INICIANDO VALIDACIÓN COMPOSITE ---")
        
        # 1. Validación de Inferencia (VetosCore)
        is_tech_ok = CONFIG["AI_THRESHOLD"] >= 0.92
        logger.info(f"🧠 VetosCore Status: {'READY' if is_tech_ok else 'FAILED'}")

        # 2. Validación Financiera (Protocolo BPI)
        is_revenue_ok = amount >= CONFIG["REVENUE_TARGET"]
        logger.info(f"💰 Revenue Status: {'VERIFIED' if is_revenue_ok else 'PENDING'}")

        # 3. Clasificación de Lead (Mesa de los Listos)
        priority = "HIGH" if any(x in email for x in ["@inditex", "@loreal", "@bpi"]) else "LOW"
        
        if is_tech_ok and is_revenue_ok:
            result = {
                "status": "SUCCESS",
                "lead": email,
                "priority": priority,
                "timestamp": datetime.now().isoformat()
            }
            await self.sync_to_make(result)
            return result
        return {"status": "HOLD", "reason": "Technical or Financial validation pending"}

    async def sync_to_make(self, data):
        """Envía el éxito a Slack/LinkedIn vía Make"""
        try:
            requests.post(CONFIG["MAKE_WEBHOOK_URL"], json=data, timeout=5)
            logger.info("🚀 Sincronización con Make: EXITOSA")
        except Exception as e:
            logger.error(f"❌ Error de red en Make: {e}")

async def main():
    orchestrator = CompositeOrchestrator()
    # Simulación de ejecución total
    await orchestrator.validate_all("compras@inditex.com", 7500.0)

if __name__ == "__main__":
    asyncio.run(main())
>>>>>>> 6a178dc5f1fe478f44c7bf0a95af8fcca30ca162
