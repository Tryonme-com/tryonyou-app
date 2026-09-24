"""TryOnYou Omega API — demo local. Arranque: uvicorn backend.omega_core:app --reload --port 8000"""
from __future__ import annotations

import time

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="TRYONYOU OMEGA API")


class MirrorOrchestrator:
    def __init__(self) -> None:
        self.version = "10.5-Soberania"
        self.precision = 0.984
        self.brand = "Balmain"

    def execute_snap(self, user_id: str) -> dict:
        time.sleep(0.05)
        time.sleep(0.05)
        return {
            "status": "SUCCESS",
            "user_id": user_id,
            "look_applied": f"{self.brand} Structured Blazer",
            "precision_achieved": f"{self.precision * 100:.1f}%",
            # No usar prefijos tipo cs_live_ en demo (confunde con Stripe real).
            "checkout_demo_ref": f"demo_checkout_{self.brand.lower()}_{int(time.time())}",
        }


orchestrator = MirrorOrchestrator()


class SnapBody(BaseModel):
    user_id: str = "VIP_001"


@app.post("/api/snap")
async def trigger_snap(body: SnapBody = SnapBody()) -> dict:
    return orchestrator.execute_snap(body.user_id)


@app.get("/health")
async def health() -> dict:
    return {"ok": True, "version": orchestrator.version}
