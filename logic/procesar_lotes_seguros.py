"""
Fragmentacion de montos en lotes monitorizables (ejecucion tipo Jules).

Exporta CSV via pandas. Ruta: variable REGISTRO_PAGOS_CSV o por defecto
registro_pagos_hoy.csv en el directorio de trabajo actual.

Patente PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberania V10 - Founder: Ruben
"""

from __future__ import annotations

import datetime
import os
import random
from typing import Any, Final

import pandas as pd

LIMITE_MAXIMO_ACUMULADO_EUR: Final[float] = 430_000.0
_FRAGMENTO_MIN_EUR: Final[int] = 2_000


def procesar_lotes_seguros(
    monto_objetivo: float,
    limite_por_pago: int,
    acumulado_total: float,
) -> list[dict[str, Any]]:
    if monto_objetivo < 0:
        raise ValueError("monto_objetivo no puede ser negativo")
    if acumulado_total < 0:
        raise ValueError("acumulado_total no puede ser negativo")
    if limite_por_pago < _FRAGMENTO_MIN_EUR:
        raise ValueError(
            f"limite_por_pago debe ser >= {_FRAGMENTO_MIN_EUR} (fragmento minimo)"
        )

    objetivo = float(monto_objetivo)
    if acumulado_total + objetivo > LIMITE_MAXIMO_ACUMULADO_EUR:
        objetivo = max(0.0, LIMITE_MAXIMO_ACUMULADO_EUR - acumulado_total)

    transacciones: list[dict[str, Any]] = []
    restante = round(objetivo, 2)

    while restante > 0:
        tope_fragmento = float(random.randint(_FRAGMENTO_MIN_EUR, limite_por_pago))
        importe = min(restante, tope_fragmento)
        importe = round(importe, 2)
        if importe <= 0:
            break
        transacciones.append(
            {
                "fecha_hora": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "importe_eur": importe,
                "estado": "CONFIRMADO",
                "id_transaccion": f"DIV-{random.randint(100_000, 999_999)}",
            }
        )
        restante = round(restante - importe, 2)

    return transacciones


def main() -> None:
    monto_dia = 40_000
    fragmentacion_max = 8_000
    acumulado_previo = 0.0

    lote_ejecutado = procesar_lotes_seguros(monto_dia, fragmentacion_max, acumulado_previo)
    df_reporte = pd.DataFrame(lote_ejecutado)
    out_path = os.getenv("REGISTRO_PAGOS_CSV", "registro_pagos_hoy.csv")
    df_reporte.to_csv(out_path, index=False)
    total = float(df_reporte["importe_eur"].sum()) if not df_reporte.empty else 0.0
    print(f"Operacion completada. Total inyectado: {total} EUR. Archivo: {out_path}")


if __name__ == "__main__":
    main()
