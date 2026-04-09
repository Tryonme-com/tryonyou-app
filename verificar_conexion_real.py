"""
Comprueba que hay claves Stripe en el entorno (pk + sk) y si pk es live o test.
También verifica intentos de pago distinguiendo transferencias bancarias externas
(Bancario_Externo) de pagos que deben pasar por Stripe.

Acepta los mismos alias que inject_keys: VITE_STRIPE_PUBLIC_KEY, INJECT_*, E50_*.

No imprime secretos. No añade dependencias (sin requests).

Ejecutar: python3 verificar_conexion_real.py
"""

from __future__ import annotations

import os
import sys
from typing import Any


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


def verificar_intentos_pago(intentos_pago: list[dict[str, Any]]) -> None:
    """Verifica una lista de intentos de pago e informa sobre su ruta de procesamiento.

    Los pagos con status ``"Bancario_Externo"`` son transferencias corporativas
    directas al IBAN que no pasan por Stripe.  Cualquier otro status indica un
    pago bloqueado por falta de verificación.

    Args:
        intentos_pago: Lista de dicts con al menos las claves ``"status"``,
            ``"emisor"`` y ``"monto"``.
    """
    print("--- [VERIFICACIÓN DE CONEXIÓN] ---")
    for pago in intentos_pago:
        if pago["status"] == "Bancario_Externo":
            print(f"AVISO: El pago de {pago['emisor']} NO pasará por la App de Stripe.")
            print(f"MOTIVO: Transferencia corporativa directa al IBAN.")
        else:
            print(f"ERROR: Pago de {pago['monto']}€ bloqueado por falta de verificación.")


if __name__ == "__main__":
    ok = verificar_conexion_real()
    sys.exit(0 if ok else 1)
