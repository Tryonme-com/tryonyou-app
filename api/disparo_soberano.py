"""
Compatibilidad: la liquidación Stripe Hito 2 / SacMuseum vive en ``scripts/sacmuseum_h2_stripe.py``.

No almacenar claves ni lógica de payout en este módulo; usar variables de entorno y el script documentado.

Patente: PCT/EP2025/067317 — Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""

from __future__ import annotations


def main() -> None:
    print(
        "api/disparo_soberano.py — usar desde la raíz del repo:\n"
        "  python3 scripts/sacmuseum_h2_stripe.py\n"
        "  STRIPE_PAYOUT_CONFIRM=1 python3 scripts/sacmuseum_h2_stripe.py\n"
        "Ver docstring de ese script (STRIPE_SECRET_KEY_FR, STRIPE_ACCOUNT_ID, etc.)."
    )


if __name__ == "__main__":
    main()
