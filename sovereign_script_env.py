"""
Credenciales para scripts locales TryOnYou — nunca hardcodear secretos en el repo.

- Stripe: STRIPE_SECRET_KEY_FR (Paris); luego STRIPE_SECRET_KEY_NUEVA / STRIPE_SECRET_KEY (migración).
- SMTP: EMAIL_USER + EMAIL_PASS (o E50_SMTP_USER / E50_SMTP_PASS).

Patente PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import os
import sys


def resolve_stripe_secret_for_script() -> str:
    sk = (
        os.environ.get("STRIPE_SECRET_KEY_FR", "").strip()
        or os.environ.get("STRIPE_SECRET_KEY_NUEVA", "").strip()
        or os.environ.get("STRIPE_SECRET_KEY", "").strip()
    )
    if sk:
        return sk
    try:
        from stripe_verify_secret_env import resolve_stripe_secret

        return resolve_stripe_secret()
    except Exception:
        return ""


def require_stripe_secret() -> str:
    sk = resolve_stripe_secret_for_script()
    if not sk:
        print(
            "Define STRIPE_SECRET_KEY_FR (Paris) en entorno (nunca en código).",
            file=sys.stderr,
        )
        sys.exit(2)
    return sk


def resolve_smtp_credentials() -> tuple[str, str]:
    user = (
        os.environ.get("EMAIL_USER", "").strip()
        or os.environ.get("SENDER_EMAIL", "").strip()
        or os.environ.get("E50_SMTP_USER", "").strip()
    )
    pw = (
        os.environ.get("EMAIL_PASS", "").strip()
        or os.environ.get("E50_SMTP_PASS", "").strip()
    )
    return user, pw


def require_smtp_credentials() -> tuple[str, str]:
    u, p = resolve_smtp_credentials()
    if not u or not p:
        print(
            "SMTP: define EMAIL_USER y EMAIL_PASS (o alias .env.example).",
            file=sys.stderr,
        )
        sys.exit(2)
    return u, p


def reply_to_from_env(sender: str) -> str:
    return (
        os.environ.get("REPLY_TO_EMAIL", "").strip()
        or os.environ.get("REMITENTE", "").strip()
        or sender
    )
