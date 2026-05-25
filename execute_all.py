from __future__ import annotations

import json
import os
import signal
import sys
from typing import Any

from balance_soberana import run_balance_sync
from payment_gateway import create_health_status_server, build_gateway_payload


def execute_pipeline() -> dict[str, Any]:
    return build_gateway_payload([run_balance_sync()])


def _resolve_port() -> int:
    raw_port = os.environ.get("PORT", "8000").strip()
    port = int(raw_port)
    if port <= 0 or port > 65535:
        raise ValueError("PORT debe estar entre 1 y 65535")
    return port


def main() -> int:
    payload = execute_pipeline()
    host = os.environ.get("HOST", "0.0.0.0").strip() or "0.0.0.0"

    try:
        port = _resolve_port()
    except ValueError as exc:
        print(f"[execute_all] Configuración inválida: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(payload, ensure_ascii=False), flush=True)
    server = create_health_status_server(payload, host=host, port=port)
    loopback_host = "localhost" if host == "0.0.0.0" else host
    print(f"[execute_all] Endpoint listo en http://{loopback_host}:{port}/health-status", flush=True)

    def shutdown(*_: object) -> None:
        server.shutdown()

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    try:
        server.serve_forever()
    finally:
        server.server_close()

    return 0 if payload["ready"] else 1


if __name__ == "__main__":
    sys.exit(main())
