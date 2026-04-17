"""Harness retirado: no simular payouts ni escribir estado financiero falso."""

from __future__ import annotations


def disparo_final_status() -> dict[str, str]:
    """Solo metadatos; sin efectos secundarios."""
    return {
        "module": "tests.disparo_final",
        "status": "disabled_harness",
        "note": "Liquidaciones reales solo en Stripe/banco con revisión humana.",
    }


if __name__ == "__main__":
    print(disparo_final_status())
