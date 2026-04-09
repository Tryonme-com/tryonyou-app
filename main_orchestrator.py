"""Main Orchestrator — TryOnYou V10 background agent runner.

Designed to be launched with:
    nohup python3 main_orchestrator.py > agentes.log 2>&1 &

Coordinates the key subsystems:
  - Robert Engine   : biometric fit processing
  - Sovereign Sale  : end-to-end sale flow
  - Peacock Core    : webhook guard + latency rules
  - Billing engine  : Stripe product/settlement status check

Patente: PCT/EP2025/067317
SIREN:   943 610 196
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent

# Make sure api/ is importable when running from repo root
_API = str(ROOT / "api")
if _API not in sys.path:
    sys.path.insert(0, _API)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

PATENT = "PCT/EP2025/067317"
VERSION = "V10-MAIN-ORCHESTRATOR"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ts() -> str:
    """Return a UTC timestamp string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _log(module: str, msg: str) -> None:
    print(f"[{_ts()}] [{module}] {msg}", flush=True)


# ---------------------------------------------------------------------------
# Agent modules
# ---------------------------------------------------------------------------

def run_peacock_core() -> dict[str, Any]:
    """Validate Peacock Core rules and return a status dict."""
    from peacock_core import ZERO_SIZE_LATENCY_BUDGET_MS, is_webhook_destination_forbidden

    _log("PEACOCK_CORE", f"Latency budget: {ZERO_SIZE_LATENCY_BUDGET_MS} ms")
    forbidden_example = "https://api.abvetos.com/hook/test"
    is_blocked = is_webhook_destination_forbidden(forbidden_example)
    _log("PEACOCK_CORE", f"Forbidden-webhook guard active: {is_blocked}")
    return {
        "status": "OK",
        "latency_budget_ms": ZERO_SIZE_LATENCY_BUDGET_MS,
        "webhook_guard": is_blocked,
    }


def run_robert_engine(fabric_key: str = "BALMAIN-WHITE-SNAP") -> dict[str, Any]:
    """Run a demo frame through Robert Engine and return the fit report."""
    from robert_engine import RobertEngine, UserAnchors

    engine = RobertEngine()
    _log("ROBERT_ENGINE", f"Status: {engine.status}")
    anchors = UserAnchors(shoulder_w=420.0, hip_y=960.0)
    fit_report = engine.process_frame(
        fabric_key,
        anchors.shoulder_w,
        anchors.hip_y,
        100,
        {"w": 1080, "h": 1920},
    )
    _log("ROBERT_ENGINE", f"Fit verdict: {fit_report.get('verdict')} | Score: {fit_report.get('fit_score')}")
    return fit_report


def run_sovereign_sale(fabric_key: str = "BALMAIN-WHITE-SNAP") -> dict[str, Any]:
    """Execute a sovereign sale flow and return the result."""
    from franchise_contract import FranchiseContract
    from robert_engine import UserAnchors
    from shopify_bridge import ShopifyBridge
    from sovereign_sale import execute_sovereign_sale

    franchise = FranchiseContract()
    shopify = ShopifyBridge()
    anchors = UserAnchors(shoulder_w=420.0, hip_y=960.0)
    result = execute_sovereign_sale(franchise, shopify, anchors, fabric_key)
    _log(
        "SOVEREIGN_SALE",
        f"Status: {result.get('sale_status')} | Commission: {result.get('franchise_commission')} €",
    )
    return result


def run_billing_status() -> dict[str, Any]:
    """Check billing engine environment and return a status summary."""
    stripe_key_present = bool(os.environ.get("STRIPE_SECRET_KEY", "").strip())
    _log("BILLING", f"Stripe key present: {stripe_key_present}")
    return {
        "status": "OK",
        "stripe_key_present": stripe_key_present,
    }


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main() -> int:
    """Run all agent modules once and print a summary."""
    _log("MAIN_ORCHESTRATOR", f"=== {VERSION} — {PATENT} ===")
    _log("MAIN_ORCHESTRATOR", "Starting agent sequence...")

    results: dict[str, Any] = {}

    try:
        results["peacock_core"] = run_peacock_core()
    except Exception as exc:  # noqa: BLE001
        _log("PEACOCK_CORE", f"ERROR: {exc}")
        results["peacock_core"] = {"status": "ERROR", "error": str(exc)}

    try:
        results["robert_engine"] = run_robert_engine()
    except Exception as exc:  # noqa: BLE001
        _log("ROBERT_ENGINE", f"ERROR: {exc}")
        results["robert_engine"] = {"status": "ERROR", "error": str(exc)}

    try:
        results["sovereign_sale"] = run_sovereign_sale()
    except Exception as exc:  # noqa: BLE001
        _log("SOVEREIGN_SALE", f"ERROR: {exc}")
        results["sovereign_sale"] = {"status": "ERROR", "error": str(exc)}

    try:
        results["billing"] = run_billing_status()
    except Exception as exc:  # noqa: BLE001
        _log("BILLING", f"ERROR: {exc}")
        results["billing"] = {"status": "ERROR", "error": str(exc)}

    # Summary
    errors = [k for k, v in results.items() if v.get("status") == "ERROR"]
    if errors:
        _log("MAIN_ORCHESTRATOR", f"Completed with errors in: {', '.join(errors)}")
        return 1

    _log("MAIN_ORCHESTRATOR", "All agents completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
