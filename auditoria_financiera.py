"""
Auditoría financiera TryOnYou — balance y últimos payouts via Stripe API.

Lee la clave Stripe desde el entorno (NUNCA hardcodear credenciales en el código).

Orden de resolución de clave:
  STRIPE_SECRET_KEY_FR → STRIPE_SECRET_KEY_NUEVA → STRIPE_SECRET_KEY

Uso:
  export STRIPE_SECRET_KEY_FR=sk_live_...
  python3 auditoria_financiera.py

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import sys
from typing import Any

from stripe_verify_secret_env import resolve_stripe_secret

PAYOUT_LIMIT = 5


def obtener_auditoria_financiera(*, sk: str | None = None) -> dict[str, Any]:
    """Retorna un resumen de auditoría con saldo disponible y últimos payouts.

    Parameters
    ----------
    sk : str, optional
        Clave secreta Stripe. Si se omite, se resuelve desde el entorno.

    Returns
    -------
    dict con claves:
        ok              – True si la auditoría fue exitosa
        saldo_disponible – importe disponible en EUR (float) o None
        payouts         – lista de dicts con id, amount_eur y status
        error           – mensaje de error si ok es False
    """
    key = sk or resolve_stripe_secret()
    if not key:
        return {
            "ok": False,
            "saldo_disponible": None,
            "payouts": [],
            "error": (
                "Define STRIPE_SECRET_KEY_FR (o STRIPE_SECRET_KEY_NUEVA / "
                "STRIPE_SECRET_KEY) en el entorno."
            ),
        }

    try:
        import stripe  # type: ignore
    except ImportError:
        return {
            "ok": False,
            "saldo_disponible": None,
            "payouts": [],
            "error": "Falta dependencia 'stripe'. Ejecuta: pip install stripe",
        }

    stripe.api_key = key

    try:
        balance = stripe.Balance.retrieve()
        available = getattr(balance, "available", None) or balance.get("available", [])
        eur_entry = next(
            (x for x in available if (x.get("currency") or "").lower() == "eur"),
            available[0] if available else None,
        )
        saldo_disponible: float | None = (
            int(eur_entry.get("amount", 0)) / 100.0 if eur_entry else None
        )
    except Exception as exc:
        return {
            "ok": False,
            "saldo_disponible": None,
            "payouts": [],
            "error": f"Error al leer Balance: {exc}",
        }

    try:
        payout_list = stripe.Payout.list(limit=PAYOUT_LIMIT)
        payouts = [
            {
                "id": p.id,
                "amount_eur": p.amount / 100.0,
                "status": p.status,
            }
            for p in payout_list.data
        ]
    except Exception as exc:
        return {
            "ok": False,
            "saldo_disponible": saldo_disponible,
            "payouts": [],
            "error": f"Error al listar Payouts: {exc}",
        }

    return {
        "ok": True,
        "saldo_disponible": saldo_disponible,
        "payouts": payouts,
        "error": "",
    }


def _imprimir_auditoria(result: dict[str, Any]) -> None:
    print("--- Auditoría TryOnYou ---")
    if not result["ok"]:
        print(f"Error en la auditoría: {result['error']}", file=sys.stderr)
        return
    saldo = result["saldo_disponible"]
    if saldo is not None:
        print(f"Saldo disponible: {saldo:.2f} EUR")
    print("Últimos movimientos (Payouts):")
    for p in result["payouts"]:
        print(f"- ID: {p['id']} | Importe: {p['amount_eur']:.2f} EUR | Estado: {p['status']}")


def main() -> int:
    result = obtener_auditoria_financiera()
    _imprimir_auditoria(result)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
