"""
Auditoría de impacto matinal V10 — verificación de clearing bancario (Lafayette / LVMH).

Incluye dos flujos complementarios:
  - check_bank_impact()          → auditoría de ingresos esperados (resumen diario).
  - check_immediate_liquidity()  → monitor de liquidez SEPA en tiempo real (minuto a minuto).

  python3 auditoria_impacto_matinal.py             # auditoría completa (ambos flujos)
  python3 auditoria_impacto_matinal.py --liquidez   # solo monitor de liquidez SEPA

  # Envío al centinela Telegram:
  export AUDIT_SEND_TELEGRAM=1
  export TELEGRAM_BOT_TOKEN='…'   # o TELEGRAM_TOKEN
  export TELEGRAM_CHAT_ID='…'
  python3 auditoria_impacto_matinal.py

Patente: PCT/EP2025/067317
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime
from typing import Any, Dict, List

SIREN_REF = "943 610 196"
SIRET_REF = "94361019600017"
CLEARING_HOUR = 9
OBJETIVO_TOTAL = 405_680.00
TARGET_INVOICE_AMOUNTS_CENTS: Dict[int, str] = {
    2_750_000: "Lafayette",
    2_250_000: "LVMH",
}
RETRYABLE_RECONCILIATION_STATUSES = {"open", "processing"}

INGRESOS_ESPERADOS: List[Dict[str, object]] = [
    {"origen": "Lafayette", "importe": 27_500.00},
    {"origen": "LVMH", "importe": 22_500.00},
]


def check_bank_impact(*, now: datetime | None = None) -> dict:
    """Return a structured audit result for the morning bank clearing window.

    Parameters
    ----------
    now : datetime, optional
        Override for the current timestamp (useful for testing).

    Returns
    -------
    dict with keys:
        status     – human-readable status line
        clearing   – True if the clearing window has passed
        objetivo   – target total in EUR
        ingresos   – list of expected line items
        timestamp  – ISO-formatted audit time
    """
    ahora = now or datetime.now()

    clearing_done = ahora.hour >= CLEARING_HOUR

    if clearing_done:
        estado = (
            "ESTADO: Revisa tu App Bancaria AHORA. "
            "El clearing ha finalizado."
        )
    else:
        minutos_restantes = (CLEARING_HOUR - ahora.hour - 1) * 60 + (60 - ahora.minute)
        estado = (
            f"ESTADO: Faltan {minutos_restantes} minutos "
            f"para el barrido bancario de las {CLEARING_HOUR:02d}:00."
        )

    return {
        "status": estado,
        "clearing": clearing_done,
        "objetivo": OBJETIVO_TOTAL,
        "ingresos": INGRESOS_ESPERADOS,
        "timestamp": ahora.isoformat(),
    }


SEPA_SWEEP_MARGIN_MINUTES = 15


def _to_int_or_none(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _infer_invoice_amount_cents(invoice: dict[str, Any]) -> int | None:
    """Return the best integer-cent amount available from a Stripe invoice object."""
    candidates: list[int] = []
    for key in ("total", "amount_due", "amount_remaining"):
        parsed = _to_int_or_none(invoice.get(key))
        if parsed is not None and parsed >= 0:
            candidates.append(parsed)
    if not candidates:
        return None
    return max(candidates)


def _infer_invoice_status(invoice: dict[str, Any]) -> str:
    """Normalize Stripe invoice status, falling back to payment_intent status."""
    status = str(invoice.get("status") or "").strip().lower()
    if status:
        return status
    payment_intent = invoice.get("payment_intent")
    if isinstance(payment_intent, dict):
        pi_status = str(payment_intent.get("status") or "").strip().lower()
        if pi_status:
            return pi_status
    return "unknown"


def _build_reconciliation_metadata(
    *,
    existing_metadata: dict[str, Any] | None,
    amount_cents: int,
    origin: str,
) -> dict[str, str]:
    base = dict(existing_metadata or {})
    base.update(
        {
            "siren": SIREN_REF.replace(" ", ""),
            "siren_display": SIREN_REF,
            "siret": SIRET_REF,
            "target_amount_cents": str(amount_cents),
            "target_origin": origin,
            "reconciliation_phase": "aggressive_retry_v10",
        }
    )
    return {str(k): str(v) for k, v in base.items()}


def aggressive_invoice_reconciliation(*, now: datetime | None = None) -> dict[str, Any]:
    """Sweep Stripe invoices and force immediate retry for target invoices."""
    timestamp = (now or datetime.now()).isoformat()
    sk = (os.environ.get("STRIPE_SECRET_KEY") or "").strip()
    if not sk.startswith(("sk_live_", "sk_test_")):
        return {
            "timestamp": timestamp,
            "ok": False,
            "status": "stripe_secret_missing_or_invalid",
            "error": "Define STRIPE_SECRET_KEY con prefijo sk_live_ o sk_test_.",
            "scanned": 0,
            "matched": 0,
            "retried": 0,
            "errors": 0,
            "items": [],
        }

    try:
        import stripe  # type: ignore
    except ImportError:
        return {
            "timestamp": timestamp,
            "ok": False,
            "status": "stripe_sdk_missing",
            "error": "Falta dependencia 'stripe' en el entorno actual.",
            "scanned": 0,
            "matched": 0,
            "retried": 0,
            "errors": 0,
            "items": [],
        }

    stripe.api_key = sk
    items: list[dict[str, Any]] = []
    scanned = 0
    matched = 0
    retried = 0
    errors = 0

    try:
        listed = stripe.Invoice.list(limit=100)
        for invoice in listed.auto_paging_iter():
            scanned += 1
            amount_cents = _infer_invoice_amount_cents(invoice)
            if amount_cents is None:
                continue
            origin = TARGET_INVOICE_AMOUNTS_CENTS.get(amount_cents)
            if not origin:
                continue

            matched += 1
            invoice_id = str(invoice.get("id") or "")
            status = _infer_invoice_status(invoice)
            item: dict[str, Any] = {
                "invoice_id": invoice_id or "unknown",
                "origin": origin,
                "amount_cents": amount_cents,
                "status": status,
            }

            if status not in RETRYABLE_RECONCILIATION_STATUSES:
                item["action"] = "skip_non_retryable_status"
                items.append(item)
                continue

            try:
                metadata = _build_reconciliation_metadata(
                    existing_metadata=invoice.get("metadata"),
                    amount_cents=amount_cents,
                    origin=origin,
                )
                stripe.Invoice.modify(invoice_id, metadata=metadata)
                paid = stripe.Invoice.pay(invoice_id)
                item["action"] = "forced_retry_sent"
                item["new_status"] = _infer_invoice_status(paid)
                retried += 1
            except Exception as exc:  # pragma: no cover - network/SDK side effects
                errors += 1
                item["action"] = "forced_retry_failed"
                item["error"] = str(exc)

            items.append(item)
    except Exception as exc:  # pragma: no cover - network/SDK side effects
        return {
            "timestamp": timestamp,
            "ok": False,
            "status": "stripe_invoice_scan_failed",
            "error": str(exc),
            "scanned": scanned,
            "matched": matched,
            "retried": retried,
            "errors": errors + 1,
            "items": items,
        }

    return {
        "timestamp": timestamp,
        "ok": errors == 0,
        "status": "done" if errors == 0 else "done_with_errors",
        "error": "",
        "scanned": scanned,
        "matched": matched,
        "retried": retried,
        "errors": errors,
        "items": items,
    }


def check_immediate_liquidity(*, now: datetime | None = None) -> dict:
    """Real-time SEPA liquidity monitor relative to the 09:00 clearing window.

    Parameters
    ----------
    now : datetime, optional
        Override for the current timestamp (useful for testing).

    Returns
    -------
    dict with keys:
        status          – human-readable status line
        sweep_started   – True once the SEPA sweep hour has passed
        minutes_left    – minutes until sweep (0 when sweep_started is True)
        timestamp       – ISO-formatted monitor time
    """
    ahora = now or datetime.now()
    target_time = ahora.replace(hour=CLEARING_HOUR, minute=0, second=0, microsecond=0)

    if ahora < target_time:
        faltan = int((target_time - ahora).total_seconds() / 60)
        estado = (
            f"ESTADO: EN TRÁNSITO. Faltan {faltan} minutos "
            "para el barrido bancario SEPA."
        )
        return {
            "status": estado,
            "sweep_started": False,
            "minutes_left": faltan,
            "timestamp": ahora.isoformat(),
        }

    estado = (
        "ESTADO: BARRIDO INICIADO. "
        f"Revisa tu banca online en los próximos {SEPA_SWEEP_MARGIN_MINUTES} minutos."
    )
    return {
        "status": estado,
        "sweep_started": True,
        "minutes_left": 0,
        "timestamp": ahora.isoformat(),
    }


def formato_liquidez(result: dict) -> str:
    """Pretty-print the liquidity monitor result for terminal / Telegram."""
    lineas = [
        f"--- [MONITOR DE LIQUIDEZ: {result['timestamp']}] ---",
        "",
        result["status"],
        "",
        f"SIREN: {SIREN_REF}",
        "Patente: PCT/EP2025/067317",
        "Bajo Protocolo de Soberanía V10 - Founder: Rubén",
    ]
    return "\n".join(lineas)


def formato_reconciliacion(result: dict[str, Any]) -> str:
    """Pretty-print aggressive invoice reconciliation output."""
    lineas = [
        "--- [FASE DE RECONCILIACIÓN AGRESIVA] ---",
        f"🕐 Timestamp: {result.get('timestamp', '')}",
        f"Estado: {result.get('status', 'unknown')}",
    ]

    error = str(result.get("error", "") or "").strip()
    if error:
        lineas.append(f"Error: {error}")

    lineas += [
        f"Invoices escaneadas: {result.get('scanned', 0)}",
        f"Invoices objetivo (27.500€/22.500€): {result.get('matched', 0)}",
        f"Retries forzados: {result.get('retried', 0)}",
        f"Errores: {result.get('errors', 0)}",
        "",
    ]

    for item in result.get("items", []):
        lineas.append(
            f"- {item.get('invoice_id', 'unknown')} | "
            f"{item.get('origin', '?')} | "
            f"{item.get('amount_cents', '?')} cents | "
            f"status={item.get('status', '?')} | "
            f"action={item.get('action', '?')}"
        )
        if item.get("new_status"):
            lineas.append(f"  ↳ new_status={item.get('new_status')}")
        if item.get("error"):
            lineas.append(f"  ↳ error={item.get('error')}")

    lineas += [
        "",
        f"SIREN: {SIREN_REF}",
        "Patente: PCT/EP2025/067317",
        "Bajo Protocolo de Soberanía V10 - Founder: Rubén",
    ]
    return "\n".join(lineas)


def formato_consola(result: dict) -> str:
    """Pretty-print the audit result for terminal / Telegram."""
    lineas = [
        "--- [AUDITORÍA DE IMPACTO MATINAL] ---",
        f"🕐 Timestamp: {result['timestamp']}",
        f"🎯 Objetivo total: {result['objetivo']:,.2f} €",
        "",
    ]
    for ing in result["ingresos"]:
        lineas.append(f"  🔎 Buscando ingreso de: {ing['importe']:,.2f} € ({ing['origen']})")

    lineas += [
        "",
        f"📊 Clearing (>= {CLEARING_HOUR:02d}:00): {'SÍ' if result['clearing'] else 'NO'}",
        result["status"],
        "",
        f"SIREN: {SIREN_REF}",
        "Patente: PCT/EP2025/067317",
        "Bajo Protocolo de Soberanía V10 - Founder: Rubén",
    ]
    return "\n".join(lineas)


def _enviar_telegram(texto: str) -> bool:
    token = (
        os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
        or os.environ.get("TELEGRAM_TOKEN", "").strip()
    )
    chat = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat:
        print(
            "❌ AUDIT_SEND_TELEGRAM=1 pero faltan token o chat_id.",
            file=sys.stderr,
        )
        return False
    try:
        import requests
    except ImportError:
        print("❌ pip install requests", file=sys.stderr)
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        r = requests.post(
            url,
            json={"chat_id": chat, "text": texto},
            timeout=30,
        )
        if r.status_code == 200:
            print("✅ Auditoría enviada a Telegram.")
            return True
        print(f"❌ Telegram HTTP {r.status_code}: {r.text[:300]}", file=sys.stderr)
    except Exception as e:
        print(f"❌ Telegram: {e}", file=sys.stderr)
    return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Auditoría de impacto matinal V10 — clearing bancario Lafayette/LVMH.",
    )
    parser.add_argument(
        "--liquidez",
        action="store_true",
        help="Solo muestra el monitor de liquidez SEPA (sin auditoría completa).",
    )
    parser.add_argument(
        "--reconciliar-agresivo",
        action="store_true",
        help=(
            "Recorre todos los invoices Stripe y fuerza retry inmediato para "
            "Lafayette 27.500€ y LVMH 22.500€ cuando estén en open/processing."
        ),
    )
    args = parser.parse_args(argv)

    bloques: list[str] = []

    if args.reconciliar_agresivo:
        recon = aggressive_invoice_reconciliation()
        bloques.append(formato_reconciliacion(recon))
        if args.liquidez:
            liq = check_immediate_liquidity()
            bloques.append(formato_liquidez(liq))
    elif args.liquidez:
        liq = check_immediate_liquidity()
        bloques.append(formato_liquidez(liq))
    else:
        result = check_bank_impact()
        bloques.append(formato_consola(result))
        liq = check_immediate_liquidity()
        bloques.append(formato_liquidez(liq))

    texto = "\n\n".join(bloques)
    print(texto)

    if os.environ.get("AUDIT_SEND_TELEGRAM", "").strip() in ("1", "true", "yes"):
        _enviar_telegram(texto)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
