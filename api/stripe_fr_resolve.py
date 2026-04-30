"""
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
