from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
API_DIR = ROOT / "api"
for candidate in (ROOT, API_DIR):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from bunker_sync import bunker_sync_status, execute_bunker_sync  # noqa: E402


status_payload, status_code = bunker_sync_status()
print(json.dumps({"status_code": status_code, "status_payload": status_payload}, ensure_ascii=False))

sync_payload, sync_code = execute_bunker_sync({"dry_run": True})
summary = {
    "status_code": sync_code,
    "status": sync_payload.get("status"),
    "payout_lookup": sync_payload.get("payout", {}).get("lookup", {}).get("lookup"),
    "payout_found": sync_payload.get("payout", {}).get("lookup", {}).get("found"),
    "payment_intents_found": sync_payload.get("payment_intents", {}).get("lookup", {}).get("count"),
    "client_sync_ok": sync_payload.get("client", {}).get("ok"),
    "batch_dry_run": sync_payload.get("batch_payout_engine", {}).get("dry_run"),
    "available_to_sweep_eur": sync_payload.get("batch_payout_engine", {}).get("available_to_sweep_eur"),
}
print(json.dumps(summary, ensure_ascii=False))
