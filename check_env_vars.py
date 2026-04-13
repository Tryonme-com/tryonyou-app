"""
Comprueba variables criticas de entorno (local o CI). No imprime valores.
"""

from __future__ import annotations

import os
import sys


def check_env_vars() -> int:
    missing_required = False

    print("--- Variables requeridas ---")
    if os.environ.get("VITE_FIREBASE_API_KEY", "").strip():
        print("OK VITE_FIREBASE_API_KEY: Configurada.")
    else:
        print("!! VITE_FIREBASE_API_KEY: No detectada en entorno local.")
        missing_required = True

    stripe_pk = (
        os.environ.get("VITE_STRIPE_PUBLIC_KEY_FR", "").strip()
        or os.environ.get("VITE_STRIPE_PUBLIC_KEY", "").strip()
    )
    if stripe_pk:
        print("OK Stripe publishable: VITE_STRIPE_PUBLIC_KEY_FR o VITE_STRIPE_PUBLIC_KEY.")
    else:
        print(
            "!! Stripe publishable: falta VITE_STRIPE_PUBLIC_KEY_FR (Paris) o VITE_STRIPE_PUBLIC_KEY."
        )
        missing_required = True

    recommended = [
        "VITE_FIREBASE_PROJECT_ID",
        "VITE_FIREBASE_AUTH_DOMAIN",
        "VITE_FIREBASE_STORAGE_BUCKET",
        "VITE_FIREBASE_MESSAGING_SENDER_ID",
        "VITE_FIREBASE_APP_ID",
    ]
    print("\n--- Firebase Vite (recomendadas) ---")
    for var in recommended:
        if os.environ.get(var, "").strip():
            print(f"OK {var}: Configurada.")
        else:
            print(f"-- {var}: No detectada en entorno local.")

    return 1 if missing_required else 0


if __name__ == "__main__":
    sys.exit(check_env_vars())
