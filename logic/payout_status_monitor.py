"""
Vigilancia de estado de payout Empire (polling simulado o callback real).

Por defecto, al ejecutar como script se usa un demo corto (no bloquea horas).
Para bucle largo en producción/simulación: `EMPIRE_PAYOUT_MONITOR_FOREVER=1`.

Patente PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import os
import sys
import time
from collections.abc import Callable
from typing import Final

try:
    from logic.empire_live_mode import is_empire_live
except ImportError:
    from empire_live_mode import is_empire_live

_DEFAULT_TARGET_EUR: Final[int] = 27500
_DEFAULT_POLL_SEC: Final[float] = 60.0
_DEMO_POLL_SEC: Final[float] = 2.0
_DEMO_SUCCESS_AFTER_POLLS: Final[int] = 3


def monitor_and_alert(
    *,
    target_amount: int = _DEFAULT_TARGET_EUR,
    poll_interval_sec: float = _DEFAULT_POLL_SEC,
    fetch_status: Callable[[], str] | None = None,
    demo_success_after_polls: int | None = None,
) -> bool:
    """
    Hace polling hasta `SUCCESS`. Devuelve True si confirma; False no se usa hoy (bucle infinito si nunca hay éxito).

    `fetch_status` debe devolver en mayúsculas p. ej. ``"PENDING"``, ``"SUCCESS"``.
    Si `demo_success_after_polls` está definido, tras ese número de vueltas fuerza ``SUCCESS`` (solo demo/tests).
    En ``EMPIRE_MODE=REAL_MONEY_ONLY`` no se permite forzar éxito demo (lanza ``RuntimeError``).
    """
    if demo_success_after_polls is not None and is_empire_live():
        raise RuntimeError(
            "demo_success_after_polls no permitido con EMPIRE_MODE=REAL_MONEY_ONLY; "
            "use fetch_status real o desactive modo LIVE."
        )
    payout_confirmed = False
    polls = 0

    def _read_status() -> str:
        nonlocal polls
        polls += 1
        if demo_success_after_polls is not None and polls >= demo_success_after_polls:
            return "SUCCESS"
        if fetch_status is not None:
            return fetch_status().strip().upper()
        return "PENDING"

    while not payout_confirmed:
        status = _read_status()
        if status == "SUCCESS":
            payout_confirmed = True
            print(f"FONDOS DETECTADOS ({target_amount} EUR). AVISANDO AL CEO.")
            return True
        time.sleep(max(poll_interval_sec, 0.1))

    return False


def main() -> int:
    forever = os.getenv("EMPIRE_PAYOUT_MONITOR_FOREVER", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )
    poll_sec = float(os.getenv("EMPIRE_PAYOUT_POLL_SEC", str(_DEFAULT_POLL_SEC)))

    if is_empire_live() and not forever:
        print(
            "EMPIRE_MODE LIVE: el demo corto está desactivado. "
            "Exporte EMPIRE_PAYOUT_MONITOR_FOREVER=1 para polling real (y conecte fetch_status en código).",
            file=sys.stderr,
        )
        return 2

    if forever:
        print(
            "Modo EMPIRE_PAYOUT_MONITOR_FOREVER: polling cada "
            f"{poll_sec}s; defina fetch_status desde otro módulo para salida real.",
            file=sys.stderr,
        )
        monitor_and_alert(poll_interval_sec=poll_sec, demo_success_after_polls=None)
        return 0

    monitor_and_alert(
        poll_interval_sec=_DEMO_POLL_SEC,
        demo_success_after_polls=_DEMO_SUCCESS_AFTER_POLLS,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
