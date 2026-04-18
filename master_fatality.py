"""
Consolidación maestra — Lafayette, Le Bon Marché y red retail (escalable).

Fuente única de verificación de infra: Qonto (liquidez vía env / FinancialGuard) y Stripe
(cuenta Paris / saldo EUR, requisitos y metadatos de cuenta).

Prompt maestro (Cursor): confirmar cambios operativos contra este script. Nuevas entradas
de dossier / retail → ampliar CONTACTOS_CLAVE. Qonto y Stripe: solo funciones de lectura
con variables de entorno; nunca claves hardcodeadas.

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# --- Contactos y operaciones (única lista extensible: Mango, El Corte Inglés, etc.) ---
CONTACTOS_CLAVE: dict[str, dict[str, Any]] = {
    "galeries_lafayette": {
        "label": "Galeries Lafayette — piloto / espejo digital",
        "role": "retail_pilot",
        "city": "Paris",
    },
    "le_bon_marche": {
        "label": "Le Bon Marché",
        "role": "retail_reference",
        "city": "Paris",
    },
    # Añadir aquí nuevas entradas de dossier (p. ej. "mango", "el_corte_ingles").
}


def _eur_available_cents(balance_obj: Any) -> int | None:
    for bucket in getattr(balance_obj, "available", []) or []:
        if getattr(bucket, "currency", "").lower() == "eur":
            return int(getattr(bucket, "amount", 0) or 0)
    return None


def verificar_qonto() -> dict[str, Any]:
    """Liquidez y deuda: misma lógica que api/financial_guard (solo lectura env)."""
    from api.financial_guard import sovereignty_status

    return sovereignty_status()


def verificar_stripe() -> dict[str, Any]:
    """
    Saldo EUR disponible en Stripe + estado de cuenta (requisitos, metadatos).
    No imprime secretos ni claves completas.
    """
    import stripe

    from stripe_fr_resolve import resolve_stripe_secret_fr

    sk = resolve_stripe_secret_fr()
    if not sk.strip():
        return {
            "ok": False,
            "error": "missing_stripe_secret",
            "hint": "Definir STRIPE_SECRET_KEY_FR (u otras resueltas por stripe_fr_resolve).",
        }

    stripe.api_key = sk
    out: dict[str, Any] = {"ok": True, "key_prefix": sk[:7] + "…"}

    try:
        bal = stripe.Balance.retrieve()
        out["balance_eur_available_cents"] = _eur_available_cents(bal)
        acct = stripe.Account.retrieve()
        req = getattr(acct, "requirements", None)
        meta = getattr(acct, "metadata", None) or {}
        out["account_id"] = getattr(acct, "id", None)
        out["charges_enabled"] = getattr(acct, "charges_enabled", None)
        out["payouts_enabled"] = getattr(acct, "payouts_enabled", None)
        out["details_submitted"] = getattr(acct, "details_submitted", None)
        out["metadata_keys"] = sorted(meta.keys()) if isinstance(meta, dict) else []
        out["metadata_has_entries"] = bool(meta)
        if req is not None:
            out["requirements_currently_due"] = list(
                getattr(req, "currently_due", []) or [],
            )
            out["requirements_pending_verification"] = list(
                getattr(req, "pending_verification", []) or [],
            )
            out["requirements_disabled_reason"] = getattr(req, "disabled_reason", None)
    except Exception as e:
        return {"ok": False, "error": str(e)}

    return out


def consolidar_todo() -> dict[str, Any]:
    """Snapshot único: contactos declarativos + Qonto + Stripe."""
    return {
        "contactos_clave": CONTACTOS_CLAVE,
        "qonto_financial_guard": verificar_qonto(),
        "stripe": verificar_stripe(),
    }


def main() -> None:
    snapshot = consolidar_todo()
    print(json.dumps(snapshot, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
