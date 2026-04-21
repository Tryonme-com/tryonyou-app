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
        "  SACMUSEUM_PAYOUT_MODE=lafayette_watch python3 scripts/sacmuseum_h2_stripe.py\n"
        "  SACMUSEUM_PAYOUT_MODE=legacy_hito2 STRIPE_PAYOUT_CONFIRM=1 "
        "python3 scripts/sacmuseum_h2_stripe.py\n"
        "Modo por defecto: watch de cambios de balance y payout Lafayette automático "
        "para PI `pi_3OzL...` en estado available."
    )


if __name__ == "__main__":
    main()
