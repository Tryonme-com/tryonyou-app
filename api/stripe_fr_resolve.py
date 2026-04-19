"""
Resolución de credenciales Stripe — cuenta verificada Francia (Paris) / EUR.

Orden de clave secreta (servidor y scripts):
  1) STRIPE_SECRET_KEY_FR — obligatoria en producción (evitar tubo EE.UU. bloqueado)
  2) STRIPE_SECRET_KEY_NUEVA — compatibilidad migración
  3) STRIPE_SECRET_KEY — solo legado; no usar claves de cuenta estadounidense

Connect (cobro directo en cuenta conectada FR): STRIPE_CONNECT_ACCOUNT_ID_FR=acct_…
Si está vacío, el cargo va a la cuenta titular de la clave secreta (Paris como plataforma).

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import os
from typing import Any


def resolve_stripe_secret_fr() -> str:
    return (
        os.environ.get("STRIPE_SECRET_KEY_FR", "").strip()
        or os.environ.get("STRIPE_SECRET_KEY_NUEVA", "").strip()
        or os.environ.get("STRIPE_SECRET_KEY", "").strip()
    )


def resolve_stripe_connect_account_fr() -> str:
    return (os.environ.get("STRIPE_CONNECT_ACCOUNT_ID_FR") or "").strip()


def stripe_api_call_kwargs() -> dict[str, Any]:
    """Argumentos extra para API Stripe (cobro directo Connect hacia París)."""
    acct = resolve_stripe_connect_account_fr()
    if acct.startswith("acct_"):
        return {"stripe_account": acct}
    return {}


def resolve_stripe_webhook_secret_fr() -> str:
    """Secreto de firma del endpoint configurado en Dashboard cuenta FR (whsec_…)."""
    return (os.environ.get("STRIPE_WEBHOOK_SECRET_FR") or "").strip()
