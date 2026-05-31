"""
Handler Vercel para BunkerV10 / VetosCore — POST /api/vetos_core_inference
Importa la lógica desde el módulo raíz `vetos_core_inference`.
"""
from __future__ import annotations

import asyncio
import json
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from mesa_de_los_listos import MesaDeLosListos
from vetos_core_inference import PaymentDelayError, VetosInferenceSystem


async def _process_body(body: dict) -> dict:
    system = VetosInferenceSystem()
    raw_rev = body.get("revenue_validation")
    if raw_rev is None or (isinstance(raw_rev, str) and not str(raw_rev).strip()):
        raise ValueError(
            "revenue_validation es obligatorio y debe ser numérico en el cuerpo JSON"
        )
    try:
        rev = float(raw_rev)
    except (TypeError, ValueError) as e:
        raise ValueError("revenue_validation debe ser un número válido") from e
    days_delay = int(body.get("days_delay", 0))
    await system.validate_revenue_stream(rev, days_delay)

    mesa = MesaDeLosListos()
    if not await mesa.validar_ingreso_7500(rev):
        return {
            "status": "hold",
            "module": "Santuario_V10",
            "leads_synced": False,
            "revenue_check": "below_7500",
            "reason": "payment_pending",
        }

    empire = await mesa.procesar_leads_empire(body)
    inference = await system.execute_inference(body)

    return {
        "status": "success",
        "module": "Santuario_V10",
        "leads_synced": True,
        "revenue_check": "verified_7500_ok",
        "leads_empire": empire,
        "vetos_inference": inference,
    }


class handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length) if length else b"{}"
            body = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
            body = {}

        try:
            data = asyncio.run(_process_body(body))
            status = 200
        except PaymentDelayError as e:
            data = {
                "status": "error",
                "module": "Santuario_V10",
                "leads_synced": False,
                "revenue_check": "delay_7500",
                "message": str(e),
            }
            # 503: operación no aceptada por ventana de caja / retraso (≠ 200)
            status = 503
        except ValueError as e:
            data = {
                "status": "error",
                "module": "Santuario_V10",
                "leads_synced": False,
                "revenue_check": "revenue_validation_required",
                "message": str(e),
            }
            status = 422
        except Exception as e:
            data = {
                "status": "error",
                "module": "Santuario_V10",
                "leads_synced": False,
                "revenue_check": "error",
                "message": str(e),
            }
            status = 500

        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format: str, *args: object) -> None:
        return
