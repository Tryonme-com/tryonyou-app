"""
Modo Empire LIVE: bandera global y desactivación de simulación vía entorno.

No sustituye confirmaciones explícitas (p. ej. STRIPE_PAYOUT_CONFIRM=1 en liquidación Stripe).

Patente PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import os
from typing import Final, Literal

EMPIRE_MODE_LIVE: Final[str] = "REAL_MONEY_ONLY"

_SIM_ENV_KEYS_TO_CLEAR: Final[tuple[str, ...]] = (
    "JULES_FINANCE_DRY_RUN",
    "EMPIRE_PAYOUT_MONITOR_DEMO",
)


def set_empire_to_live(*, verbose: bool = True) -> Literal["READY_FOR_CASH"]:
    """
    Fija EMPIRE_MODE=REAL_MONEY_ONLY y elimina flags de simulación habituales del proceso.

    No ejecuta transferencias: cada script (Stripe, banco) sigue pidiendo su propia confirmación.
    """
    os.environ["EMPIRE_MODE"] = EMPIRE_MODE_LIVE

    for key in _SIM_ENV_KEYS_TO_CLEAR:
        os.environ.pop(key, None)

    if verbose:
        print(
            "SISTEMA LIMPIO. Modo Empire LIVE (EMPIRE_MODE=REAL_MONEY_ONLY). "
            "Sin simulación vía JULES_FINANCE_DRY_RUN / EMPIRE_PAYOUT_MONITOR_DEMO en este proceso."
        )
    return "READY_FOR_CASH"


def is_empire_live() -> bool:
    return os.environ.get("EMPIRE_MODE", "").strip() == EMPIRE_MODE_LIVE


if __name__ == "__main__":
    set_empire_to_live()
