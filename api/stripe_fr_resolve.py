"""
<<<<<<< HEAD
Re-export de resolución Stripe FR (cuenta Paris).

Carga el módulo raíz ``stripe_fr_resolve.py`` por ruta absoluta para evitar
import circular cuando ``api/`` precede a la raíz en ``sys.path``.

Patente: PCT/EP2025/067317 — Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_impl = Path(__file__).resolve().parent.parent / "stripe_fr_resolve.py"
_spec = importlib.util.spec_from_file_location(
    "stripe_fr_resolve_root_impl",
    _impl,
)
if _spec is None or _spec.loader is None:
    raise ImportError(f"No se pudo cargar {_impl}")

_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

resolve_stripe_secret_fr = _mod.resolve_stripe_secret_fr
resolve_stripe_connect_account_fr = _mod.resolve_stripe_connect_account_fr
stripe_api_call_kwargs = _mod.stripe_api_call_kwargs
resolve_stripe_webhook_secret_fr = _mod.resolve_stripe_webhook_secret_fr

__all__ = [
    "resolve_stripe_connect_account_fr",
    "resolve_stripe_secret_fr",
    "resolve_stripe_webhook_secret_fr",
    "stripe_api_call_kwargs",
]
=======
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
>>>>>>> ea0ea5d0b13accd3b7386d0d33ce0bc7846d4852
