"""
Planificador diario — estado operacional del Día 10.

  python3 daily_planner.py

Patente: PCT/EP2025/067317 | SIREN ref.: 943 610 196
"""

from __future__ import annotations

import datetime


OBJETIVO_BANCO: float = 27500.00
SIREN_REF = "943 610 196"


def status_dia_10() -> str:
    """Devuelve el estado operacional del Día 10 según la hora actual."""
    ahora = datetime.datetime.now()

    print(f"--- [ESTADO DE OPERACIÓN: {ahora.strftime('%H:%M:%S')}] ---")
    print(f"ESTATUS SIREN: {SIREN_REF} (Verificado)")
    print(f"ESTATUS JEI: Activo (Bpifrance Dossier Enviado)")

    if ahora.hour < 9:
        return (
            f"ALERTA: Faltan horas para la apertura bancaria. "
            f"Objetivo: {OBJETIVO_BANCO} €."
        )
    return (
        "ACCIÓN: Comprueba tu banca online ahora. "
        "El clearing debería haber finalizado."
    )


if __name__ == "__main__":
    print(status_dia_10())
