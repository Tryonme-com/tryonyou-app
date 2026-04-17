"""
Comprueba que hay claves Stripe en el entorno (pk + sk) y si pk es live o test.

Acepta alias Paris primero: VITE_STRIPE_PUBLIC_KEY_FR, luego inject_keys / legado.

No imprime secretos. No añade dependencias (sin requests).

Ejecutar: python3 verificar_conexion_real.py
"""

from __future__ import annotations

import os
import sys


def _g(*names: str) -> str:
    for n in names:
        v = os.environ.get(n, "").strip()
        if v:
            return v
    return ""


def verificar_conexion_real() -> bool:
    print("🕵️‍♂️ Jules: Verificando integridad del flujo de caja...")

    pk = _g(
        "VITE_STRIPE_PUBLIC_KEY",
        "INJECT_VITE_STRIPE_PUBLIC_KEY",
        "E50_VITE_STRIPE_PUBLIC_KEY",
    )
    sk = _g("STRIPE_SECRET_KEY", "INJECT_STRIPE_SECRET_KEY", "E50_STRIPE_SECRET_KEY")

    if not pk or not sk:
        print(
            "⚠️  ERROR: Faltan claves en el entorno (pk y/o sk). "
            "Exporta VITE_STRIPE_PUBLIC_KEY y STRIPE_SECRET_KEY (o INJECT_* / E50_*)."
        )
        return False

    if "pk_live" in pk:
        print("✅ MODO REAL: publishable key en vivo (pk_live).")
    elif "pk_test" in pk:
        print("ℹ️  MODO TEST: publishable key de prueba (pk_test).")
    else:
        print("ℹ️  Publishable key presente; no reconocida como pk_live/pk_test.")

    if sk.startswith("sk_live"):
        print("✅ Secret key en vivo cargada (no se muestra).")
    elif sk.startswith("sk_test"):
        print("ℹ️  Secret key de prueba cargada (no se muestra).")
    else:
        print("ℹ️  Secret key presente; prefijo no estándar.")

    return True


if __name__ == "__main__":
    ok = verificar_conexion_real()
    sys.exit(0 if ok else 1)
