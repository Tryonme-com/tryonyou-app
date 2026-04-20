"""
Balance Soberana — Estado financiero total TryOnYou V10.

Consolida los conceptos de cobro activos del pipeline soberano:
  - atrasos_piloto   : atrasos acumulados del piloto
  - nodos_activos    : canon mensual de los nodos LVMH + Westfield
  - transferencia_ip : transferencias de propiedad intelectual (×2)
  - subvencion_bft   : soporte de innovación Bpifrance

Patente: PCT/EP2025/067317
SIREN: 943 610 196
"""

from __future__ import annotations

PATENTE = "PCT/EP2025/067317"
SIREN = "943 610 196"

# Conceptos de cobro del pipeline soberano V10 (importes en €)
ATRASOS_PILOTO: float = 69_180.00
NODO_LVMH: float = 22_500.00
NODO_WESTFIELD: float = 12_500.00
TRANSFERENCIA_IP_UNIT: float = 98_250.00
SUBVENCION_BFT: float = 226_908.00

BPIFRANCE_LEDGER = {
    "organismo": "BPIFRANCE",
    "siren": SIREN,
    "linea": "Soporte de innovación",
    "estado_anterior": "En Proceso",
    "estado_actual": "Ejecución Prioritaria",
    "importe_eur": SUBVENCION_BFT,
}


def ledger_soberano() -> dict[str, object]:
    """
    Devuelve el ledger soberano actualizado para el frente Bpifrance.

    Returns:
        Diccionario con el estado operativo vigente del soporte institucional.
    """
    nodos_activos = NODO_LVMH + NODO_WESTFIELD
    transferencia_ip = TRANSFERENCIA_IP_UNIT * 2
    total = ATRASOS_PILOTO + nodos_activos + transferencia_ip + SUBVENCION_BFT

    return {
        "patente": PATENTE,
        "siren": SIREN,
        "bpifrance": BPIFRANCE_LEDGER,
        "capital_total_reclamado_eur": round(total, 2),
    }


def balance_total_soberano() -> float:
    """
    Calcula el capital total reclamado en el pipeline de cobro soberano V10.

    Returns:
        Total en euros (float) de todos los conceptos activos.
    """
    nodos_activos = NODO_LVMH + NODO_WESTFIELD
    transferencia_ip = TRANSFERENCIA_IP_UNIT * 2

    total = ATRASOS_PILOTO + nodos_activos + transferencia_ip + SUBVENCION_BFT

    print("--- [ESTADO FINANCIERO TOTAL: TRYONYOU V10] ---")
    print(f"CAPITAL TOTAL RECLAMADO: {total:,.2f} €")
    print(
        "ESTADO: Pipeline de cobro al 100% de capacidad. "
        f"BPIFRANCE en {BPIFRANCE_LEDGER['estado_actual']}."
    )

    return total
