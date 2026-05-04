"""
Verifica clave Stripe desde el entorno (sin git automático; nunca pegar claves en el código).

Orden de resolución (modo por defecto):
  1) STRIPE_RESTRICTED_KEY (rk_live_… / rk_test_) — permisos según Dashboard
  2) STRIPE_SECRET_KEY_FR → STRIPE_SECRET_KEY_NUEVA → STRIPE_SECRET_KEY
 (prioridad Paris / EUR; no usar cuenta EE.UU. bloqueada)

Modo `--funding` / `forzar_flujo_dinero()`:
  Solo STRIPE_SECRET_KEY_NUEVA → STRIPE_SECRET_KEY (tubo banco / sk_live), ignora rk_*.

No ejecuta git: `git add .` + push automático puede subir .env y saltarse el mensaje Pau.

Uso:
  export STRIPE_SECRET_KEY=sk_live_...
  python3 stripe_verify_secret_env.py --funding

  # o clave restringida (modo completo)
  export STRIPE_RESTRICTED_KEY=rk_live_...
  python3 stripe_verify_secret_env.py

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import os
import sys


def resolve_stripe_secret() -> str:
    return (
        os.environ.get("STRIPE_SECRET_KEY_FR", "").strip()
        or os.environ.get("STRIPE_SECRET_KEY_NUEVA", "").strip()
        or os.environ.get("STRIPE_SECRET_KEY", "").strip()
    )


def resolve_api_key() -> tuple[str, str]:
    """Devuelve (clave, etiqueta) para diagnóstico."""
    rk = os.environ.get("STRIPE_RESTRICTED_KEY", "").strip()
    if rk.startswith("rk_live_") or rk.startswith("rk_test_"):
        return rk, "restricted"
    if rk:
        return rk, "restricted"
    sk = resolve_stripe_secret()
    if sk:
        return sk, "secret"
    return "", ""


def _verify_stripe_account(key: str, kind: str) -> int:
    import stripe

    stripe.api_key = key
    try:
        acct = stripe.Account.retrieve()
        aid = getattr(acct, "id", "?")
        charges = getattr(acct, "charges_enabled", None)
        print(
            f"OK — Stripe API ({kind}). account.id={aid} charges_enabled={charges!r}"
        )
    except Exception as e:
        print(
            f"No se pudo validar la clave ({kind}) con Account.retrieve: {e}",
            file=sys.stderr,
        )
        if kind == "restricted":
            print(
                "Pista: en Dashboard, edita la clave restringida y concede permisos "
                "adecuados; o usa STRIPE_SECRET_KEY (sk_live_) para esta prueba.",
                file=sys.stderr,
            )
        return 3
    return 0


def verificar_conexion() -> bool:
    """
    Verifica la conexión con Stripe recuperando el balance de la cuenta.

    Lee la clave secreta desde variables de entorno (nunca hardcodeada).
    Orden de resolución: STRIPE_SECRET_KEY_FR → STRIPE_SECRET_KEY_NUEVA → STRIPE_SECRET_KEY.

    Returns:
        True si la conexión es exitosa, False en caso de error.
    """
    import stripe

    sk = resolve_stripe_secret()
    if not sk:
        print(
            "Error: define STRIPE_SECRET_KEY_FR, STRIPE_SECRET_KEY_NUEVA o STRIPE_SECRET_KEY.",
            file=sys.stderr,
        )
        return False
    stripe.api_key = sk
    try:
        stripe.Balance.retrieve()
        print("Conexión con Stripe establecida correctamente.")
        return True
    except Exception as e:
        print(f"Error de conexión: {e}")
        return False


def main() -> int:
    key, kind = resolve_api_key()
    if not key:
        print(
            "Define STRIPE_RESTRICTED_KEY, o STRIPE_SECRET_KEY_FR / STRIPE_SECRET_KEY_NUEVA / STRIPE_SECRET_KEY.",
            file=sys.stderr,
        )
        return 1
    if kind == "secret" and key.startswith("sk_test_"):
        print(
            "Se recibió sk_test_: para cuenta verificada LIVE el flujo inaugural usa sk_live_.",
            file=sys.stderr,
        )
        return 2
    return _verify_stripe_account(key, kind)


def forzar_flujo_dinero() -> int:
    """
    Valida solo la clave secreta (cuenta con banco verificado). No lanza git.

    Tras éxito, actualiza el servidor con commit manual (mensaje con @CertezaAbsoluta,
    @lo+erestu, PCT/EP2025/067317 y protocolo V10); nunca `git add .` si .env puede colarse.
    """
    sk = resolve_stripe_secret()
    if not sk:
        print(
            "Define STRIPE_SECRET_KEY_FR (Paris) o STRIPE_SECRET_KEY_NUEVA / STRIPE_SECRET_KEY.",
            file=sys.stderr,
        )
        return 1
    if sk.startswith("sk_test_"):
        print(
            "Se recibió sk_test_: para tubo LIVE usa sk_live_.",
            file=sys.stderr,
        )
        return 2
    rc = _verify_stripe_account(sk, "secret")
    if rc == 0:
        print(
            "\nTubo verificado. Siguiente paso: commit/push manual desde Jules — sin git automático."
        )
    return rc


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("--funding", "--flujo-dinero"):
        raise SystemExit(forzar_flujo_dinero())
    raise SystemExit(main())
