"""
Composite Bunker Executor — Divineo V9 / Omega (Agente 70).

Unifica:
  - Inferencia asíncrona VetosCore (umbral 0,92)
  - Validación protocolo BPI 7 500 € (validate_revenue_stream)
  - Captura de leads en dominios estratégicos (Inditex, Zara, Station F)

Webhook Make: MAKE_WEBHOOK_URL_OMEGA o MAKE_WEBHOOK_URL (nunca hardcodear URLs).

Patente: PCT/EP2025/067317 | SIREN (ref.): 943 610 196
"""

from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass
from typing import Any, Iterable

import requests

from bunker_full_orchestrator import append_waitlist_json
from vetos_core_inference import PaymentDelayError, VetosInferenceSystem


def _truthy_env(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")


def _make_post_omega(payload: dict[str, Any]) -> bool:
    url = (
        os.getenv("MAKE_WEBHOOK_URL_OMEGA", "").strip()
        or os.getenv("MAKE_WEBHOOK_URL", "").strip()
        or os.getenv("MAKE_ESPEJO_WEBHOOK_URL", "").strip()
    )
    if not url:
        return False
    try:
        r = requests.post(url, json=payload, timeout=25)
        return 200 <= r.status_code < 300
    except OSError:
        return False


def _domain_tag(email: str) -> str | None:
    """Detecta @inditex, @zara, @stationf y variantes corporativas."""
    e = (email or "").strip().lower()
    if "@" not in e:
        return None
    domain = e.split("@", 1)[1]
    if "inditex" in domain:
        return "inditex"
    if "zara" in domain:
        return "zara"
    if "stationf" in domain:
        return "stationf"
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
      - Validación Protocolo BPI (7 500 € + retraso)
      - Lead estratégico vía Make + waitlist (append_waitlist_json)
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
        try:
            await self.system.validate_revenue_stream(revenue_eur, days_delay=days_delay)
            bp_ok = True
        except PaymentDelayError:
            bp_ok = False

        payload = {
            "id": "composite_bunker_lead",
            "module": "VetosCore",
            "email": email,
            "revenue_validation": revenue_eur,
        }
        inference = await self.system.execute_inference(payload)

        strategic = _domain_tag(email)
        tags = list(extra_tags or [])
        if strategic:
            tags.append(f"strategic:{strategic}")

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
    sample_email = os.getenv("OMEGA_TEST_EMAIL", "pilot@stationf.co")
    res = await bunker.process_lead(email=sample_email)
    print(json.dumps(res.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if not _truthy_env("OMEGA_COMPOSITE_RUN"):
        print(
            "Define OMEGA_COMPOSITE_RUN=1 para demo local "
            "(OMEGA_TEST_EMAIL opcional; MAKE_WEBHOOK_URL en .env)."
        )
    else:
        asyncio.run(_demo())
