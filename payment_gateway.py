from __future__ import annotations

import json
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Sequence
from urllib.parse import urlsplit

READY_FOR_POST = "READY_FOR_POST"
BLOCKED = "BLOCKED"
HTTP_200_OK = "HTTP 200 OK"


def build_gateway_payload(steps: Sequence[dict[str, Any]]) -> dict[str, Any]:
    normalized_steps = [dict(step) for step in steps]
    blocking_steps = [step["name"] for step in normalized_steps if step.get("status") == "error"]
    ready = len(blocking_steps) == 0
    backend_status = "SUCCESS" if ready else "BLOCKED"
    gateway_status = "CONNECTED" if ready else "DISCONNECTED"
    frontend_status = "READY" if ready else "BLOCKED"
    return {
        "orchestration": "Zion",
        "status": READY_FOR_POST if ready else BLOCKED,
        "ready": ready,
        "system_check": READY_FOR_POST if ready else BLOCKED,
        "gateway_connectivity": {
            "status": gateway_status,
            "detail": "Stripe Event Confirmed" if ready else "Stripe confirmation missing",
        },
        "backend_sync": {
            "service": "Jules",
            "status": backend_status,
        },
        "frontend": {
            "service": "Pau",
            "status": frontend_status,
        },
        "endpoint_status": HTTP_200_OK if ready else "HTTP 503 BLOCKED",
        "blocking_steps": blocking_steps,
        "steps": normalized_steps,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


class HealthStatusHandler(BaseHTTPRequestHandler):
    gateway_payload: dict[str, Any] = {}

    def do_GET(self) -> None:  # noqa: N802
        if urlsplit(self.path).path != "/health-status":
            self._send_json({"ok": False, "error": "Not found"}, status=404)
            return

        self._send_json(self.gateway_payload)

    def log_message(self, format: str, *args: object) -> None:
        return

    def _send_json(self, payload: dict[str, Any], status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def create_health_status_handler(gateway_payload: dict[str, Any]) -> type[HealthStatusHandler]:
    class BoundHealthStatusHandler(HealthStatusHandler):
        pass

    BoundHealthStatusHandler.gateway_payload = gateway_payload

    return BoundHealthStatusHandler


def create_health_status_server(
    gateway_payload: dict[str, Any],
    host: str = "0.0.0.0",
    port: int = 8000,
) -> ThreadingHTTPServer:
    handler = create_health_status_handler(gateway_payload)
    return ThreadingHTTPServer((host, port), handler)
