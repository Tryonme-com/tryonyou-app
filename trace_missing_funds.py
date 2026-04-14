#!/usr/bin/env python3
"""
Trace Missing Funds — auditoría rápida del flujo monetario Empire.

Confirma la cadena:
  1) click en botón de pago (intent)
  2) checkout Stripe exitoso
  3) payout registrado

SIRET: 94361019600017 | PCT/EP2025/067317
"""

from __future__ import annotations

import argparse
import json
import sys

from empire_payout_trans import get_flow_summary


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Valida trazabilidad de fondos desde botón de pago hasta payout.",
    )
    parser.add_argument("--flow-token", default="", help="Flow token del click de pago.")
    parser.add_argument("--session-id", default="", help="Stripe checkout session id.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Falla si falta cualquier etapa de trazabilidad.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Imprime salida JSON sin formato humano adicional.",
    )
    return parser


def _print_human(summary: dict) -> None:
    print("=== TRACE MISSING FUNDS :: EMPIRE ===")
    print(f"flow_token: {summary.get('flow_token') or '-'}")
    print(f"session_id: {summary.get('session_id') or '-'}")
    print(f"intent_logged: {summary.get('intent_logged')}")
    print(f"checkout_success_logged: {summary.get('checkout_success_logged')}")
    print(f"payout_logged: {summary.get('payout_logged')}")
    print(f"checkout_host_allowed: {summary.get('checkout_host_allowed')}")
    print(f"trace_integrity: {summary.get('trace_integrity')}")
    print(f"events_count: {summary.get('events_count')}")
    print(f"missing_steps: {', '.join(summary.get('missing_steps', [])) or 'none'}")


def main() -> int:
    args = _build_parser().parse_args()
    summary = get_flow_summary(flow_token=args.flow_token, session_id=args.session_id)
    ok = bool(summary.get("trace_integrity"))

    if args.json:
        print(json.dumps(summary, ensure_ascii=False))
    else:
        _print_human(summary)

    if args.strict and not ok:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
