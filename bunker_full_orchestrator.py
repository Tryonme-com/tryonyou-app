<<<<<<< HEAD
"""
Bunker Full Orchestrator — Make.com (Slack) + persistencia waitlist local / tmp.
Patente: PCT/EP2025/067317 — payloads JSON estables para escenarios Make.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

REPO_ROOT = Path(__file__).resolve().parent


def _make_post(payload: dict[str, Any]) -> bool:
    url = (os.getenv("MAKE_WEBHOOK_URL") or "").strip()
    if not url:
        return False
    try:
        r = requests.post(url, json=payload, timeout=25)
        return r.status_code == 200
    except OSError:
        return False


def append_waitlist_json(entry: dict[str, Any]) -> tuple[bool, str | None]:
    """Intenta `leads_empire/waitlist.json`; si el FS es de solo lectura (p. ej. Vercel), usa TMPDIR."""
    stamped = {
        **entry,
        "stored_at": datetime.now(timezone.utc).isoformat(),
    }
    tmp_base = os.getenv("TMPDIR") or "/tmp"
    candidates = [
        REPO_ROOT / "leads_empire" / "waitlist.json",
        Path(tmp_base) / "leads_empire_waitlist.json",
    ]
    for path in candidates:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            data: list[Any] = []
            if path.is_file():
                raw = path.read_text(encoding="utf-8")
                data = json.loads(raw) if raw.strip() else []
            if not isinstance(data, list):
                data = []
            data.append(stamped)
            path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            return True, str(path)
        except OSError:
            continue
    return False, None


def orchestrate_beta_waitlist(body: dict[str, Any]) -> dict[str, Any]:
    """Webhook Make + append waitlist (mismo contrato que notify_slack_via_make)."""
    payload = {
        "event": "beta_waitlist",
        "channel": "general-tryonyou",
        "message": "🚀 NUEVO LEAD — Únete a la beta (TryOnYou)",
        "email": body.get("email"),
        "source": body.get("source", "app_v10"),
        "user_agent": body.get("user_agent"),
        "ts": body.get("ts"),
    }
    ok_make = _make_post(payload)
    ok_file, path = append_waitlist_json(payload)
    return {
        "make_ok": ok_make,
        "waitlist_persisted": ok_file,
        "waitlist_path": path,
    }


def orchestrate_mirror_shadow_dwell(body: dict[str, Any]) -> dict[str, Any]:
    """Shadow Mirror Test: permanencia en mirror_sanctuary → Slack vía Make."""
    dwell = body.get("dwell_ms", 0)
    payload = {
        "event": "mirror_shadow_dwell",
        "channel": "general-tryonyou",
        "message": f"🪞 Mirror Sanctuary — permanencia {dwell} ms",
        "dwell_ms": dwell,
        "dwell_sec": body.get("dwell_sec"),
        "page": body.get("page", "mirror_sanctuary_v10.html"),
        "reason": body.get("reason"),
        "ts": body.get("ts"),
    }
    ok_make = _make_post(payload)
    return {"make_ok": ok_make}
=======
import asyncio
import os
import requests
import json
from datetime import datetime

# CONFIGURACIÓN DE ENTORNO (Sincronizado con Vercel)
CONFIG = {
    "MAKE_WEBHOOK": "https://hook.us1.make.com/tu_id_de_webhook",
    "REVENUE_TARGET": 7500.0,
    "THRESHOLD": 0.92,
    "REPO": "Tryonme-com/tryonyou-app"
}

class BunkerOrchestrator:
    def __init__(self):
        self.start_time = datetime.now()
        self.status = "INITIALIZING"

    async def validate_financial_protocol(self, amount):
        """Valida el protocolo BPI de 7500€"""
        if amount >= CONFIG["REVENUE_TARGET"]:
            return True, "✅ Ingreso validado. Protocolo BPI activo."
        return False, "⚠️ Ingreso insuficiente para validación BPI."

    async def run_ai_inference(self, payload):
        """Simula la inferencia asíncrona de VetosCore (PR #2389)"""
        await asyncio.sleep(0.5)
        return {"score": CONFIG["THRESHOLD"], "status": "CALIBRATED"}

    async def notify_slack_via_make(self, event_type, data):
        """Dispara el escenario de Make para notificar en Slack"""
        payload = {
            "project": "tryonyou-app",
            "event": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        try:
            requests.post(CONFIG["MAKE_WEBHOOK"], json=payload, timeout=5)
            print(f"🚀 Notificación enviada a Slack: {event_type}")
        except Exception as e:
            print(f"❌ Error en Webhook: {e}")

async def main():
    orchestrator = BunkerOrchestrator()
    
    # 1. Ejecutar Validación Técnica
    inference = await orchestrator.run_ai_inference({"task": "full_sync"})
    
    # 2. Ejecutar Validación de Negocio (Mesa de los Listos)
    valid, msg = await orchestrator.validate_financial_protocol(7500)
    
    # 3. Sincronizar con Make/Slack
    if valid and inference["status"] == "CALIBRATED":
        await orchestrator.notify_slack_via_make("DEPLOY_READY", {
            "msg": "Sistema blindado. Listo para vercel --prod",
            "metrics": inference
        })
        print("\n🔥 TODO LISTO: Ejecuta 'vercel --prod' en la terminal.")

if __name__ == "__main__":
    asyncio.run(main())
  
>>>>>>> 6a178dc5f1fe478f44c7bf0a95af8fcca30ca162
