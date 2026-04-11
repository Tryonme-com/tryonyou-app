"""
Stripe Financial Connections handler (auto TEST/LIVE).

Este módulo selecciona automáticamente el entorno Stripe:
- LIVE cuando la cuenta llega verificada y hay clave LIVE disponible.
- TEST en el resto de casos (si existe clave TEST).
"""

from __future__ import annotations

import os
from typing import Any, Mapping

import stripe

LIVE_MODE = "LIVE"
TEST_MODE = "TEST"

_VERIFIED_STATUSES = {"verified", "active", "approved", "live_ready"}
_DEFAULT_COUNTRIES = ("FR",)
_DEFAULT_PERMISSIONS = ("balances", "ownership", "payment_method", "transactions")


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    if isinstance(value, (int, float)):
        return bool(value)
    return False


def _is_verified_account(verified_account: Mapping[str, Any] | None) -> bool:
    if not verified_account:
        return False
    if _as_bool(verified_account.get("verified")):
        return True
    status = str(verified_account.get("status", "")).strip().lower()
    if status in _VERIFIED_STATUSES:
        return True
    if _as_bool(verified_account.get("kyc_verified")):
        return True
    return False


def _first_non_empty(env: Mapping[str, str], names: tuple[str, ...]) -> str:
    for name in names:
        value = (env.get(name) or "").strip()
        if value:
            return value
    return ""


def _resolve_live_key(env: Mapping[str, str]) -> str:
    live_key = _first_non_empty(
        env,
        (
            "STRIPE_FINANCIAL_CONNECTIONS_LIVE_SECRET_KEY",
            "STRIPE_LIVE_SECRET_KEY",
        ),
    )
    if live_key:
        return live_key

    default_secret = (env.get("STRIPE_SECRET_KEY") or "").strip()
    if default_secret.startswith("sk_live_"):
        return default_secret
    return ""


def _resolve_test_key(env: Mapping[str, str]) -> str:
    test_key = _first_non_empty(
        env,
        (
            "STRIPE_FINANCIAL_CONNECTIONS_TEST_SECRET_KEY",
            "STRIPE_TEST_SECRET_KEY",
        ),
    )
    if test_key:
        return test_key

    default_secret = (env.get("STRIPE_SECRET_KEY") or "").strip()
    if default_secret.startswith("sk_test_"):
        return default_secret
    return ""


def select_financial_connections_credentials(
    verified_account: Mapping[str, Any] | None,
    *,
    env: Mapping[str, str] | None = None,
) -> tuple[str, str]:
    """
    Elige credenciales Stripe para Financial Connections.

    Cambia automáticamente a LIVE cuando la cuenta está verificada y existe
    una clave LIVE configurada.
    """
    local_env = env or os.environ
    live_key = _resolve_live_key(local_env)
    test_key = _resolve_test_key(local_env)
    account_is_verified = _is_verified_account(verified_account)

    if account_is_verified and live_key:
        return live_key, LIVE_MODE
    if test_key:
        return test_key, TEST_MODE
    if live_key:
        return live_key, LIVE_MODE

    raise EnvironmentError(
        "Missing Stripe key. Configure STRIPE_FINANCIAL_CONNECTIONS_TEST_SECRET_KEY "
        "or STRIPE_FINANCIAL_CONNECTIONS_LIVE_SECRET_KEY (or STRIPE_TEST/LIVE_SECRET_KEY)."
    )


def _build_account_holder(verified_account: Mapping[str, Any]) -> dict[str, str]:
    injected = verified_account.get("account_holder")
    if isinstance(injected, Mapping):
        holder_type = str(injected.get("type", "")).strip().lower()
        if holder_type == "customer":
            customer = str(injected.get("customer", "")).strip()
            if customer:
                return {"type": "customer", "customer": customer}
        if holder_type == "account":
            account = str(injected.get("account", "")).strip()
            if account:
                return {"type": "account", "account": account}

    customer = (
        str(verified_account.get("customer") or verified_account.get("stripe_customer_id") or "")
        .strip()
    )
    if customer:
        return {"type": "customer", "customer": customer}

    account = (
        str(verified_account.get("account") or verified_account.get("stripe_account_id") or "")
        .strip()
    )
    if account:
        return {"type": "account", "account": account}

    raise ValueError(
        "verified_account must include account_holder credentials "
        "(customer/account or account_holder payload)."
    )


def create_financial_connections_session(
    *,
    verified_account: Mapping[str, Any] | None,
    return_url: str,
    permissions: list[str] | tuple[str, ...] | None = None,
    countries: list[str] | tuple[str, ...] | None = None,
    prefetch: list[str] | tuple[str, ...] | None = None,
    env: Mapping[str, str] | None = None,
) -> tuple[dict[str, Any], int]:
    """Crea una sesión Financial Connections con inyección de credenciales verificadas."""
    local_env = env or os.environ
    clean_return_url = (return_url or "").strip()
    if not clean_return_url:
        return {"status": "error", "message": "return_url_required"}, 400

    try:
        api_key, runtime_mode = select_financial_connections_credentials(
            verified_account, env=local_env
        )
        account_holder = _build_account_holder(verified_account or {})
    except ValueError as exc:
        return {"status": "error", "message": str(exc)}, 400
    except EnvironmentError as exc:
        return {"status": "error", "message": str(exc)}, 503

    stripe.api_key = api_key
    os.environ["STRIPE_RUNTIME_ENV"] = runtime_mode

    session_params: dict[str, Any] = {
        "account_holder": account_holder,
        "permissions": list(permissions or _DEFAULT_PERMISSIONS),
        "filters": {"countries": list(countries or _DEFAULT_COUNTRIES)},
        "return_url": clean_return_url,
    }
    if prefetch:
        session_params["prefetch"] = list(prefetch)

    try:
        session = stripe.financial_connections.Session.create(**session_params)
        session_id = session.get("id")
        client_secret = session.get("client_secret")
        return {
            "status": "ok",
            "mode": runtime_mode,
            "session_id": session_id,
            "client_secret": client_secret,
            "livemode": bool(session.get("livemode")),
        }, 200
    except stripe.error.StripeError as exc:
        return {
            "status": "error",
            "mode": runtime_mode,
            "message": str(exc.user_message or exc),
        }, 502
    except Exception as exc:
        return {"status": "error", "mode": runtime_mode, "message": str(exc)}, 502
