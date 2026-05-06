"""
Balance Soberana — Estado financiero total TryOnYou V12.

Master Ledger con dos niveles de facturación:

  NIVEL 1 — Tesorería Operativa (corto plazo):
    - atrasos_piloto   : atrasos acumulados del piloto
    - nodos_activos    : canon mensual de los nodos LVMH + Westfield
    - transferencia_ip : transferencias de propiedad intelectual (×2)
    - subvencion_bft   : soporte de innovación Bpifrance

  NIVEL 2 — Contrato Marco (24 meses):
    - F-2026-001       : Contrato marco Galeries Lafayette Haussmann
                         Licencia tecnológica + despliegue omnicanal

Patente: PCT/EP2025/067317
SIREN: 943 610 196
SIRET: 94361019600017
"""

from __future__ import annotations
from datetime import datetime, timezone

PATENTE = "PCT/EP2025/067317"
SIREN = "943 610 196"
SIRET = "94361019600017"
ENTITY = "EI - ESPINAR RODRIGUEZ, RUBEN"
IBAN = "FR761695800001576292349652"
BIC = "QNTOFRP1XXX"

# ── NIVEL 1: Tesorería Operativa (proyectos a corto plazo) ──────────
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

# ── NIVEL 2: Contrato Marco (facturación a 24 meses) ────────────────
FACTURA_F_2026_001 = {
    "numero": "F-2026-001",
    "tipo": "Contrat-Cadre / Contrato Marco",
    "cliente": "GALERIES LAFAYETTE HAUSSMANN",
    "cliente_siret": "552 129 211 00011",
    "cliente_direccion": "40 BOULEVARD HAUSSMANN, 75009 PARIS",
    "concepto": (
        "Licence technologique PauPeacockEngine V12 — Déploiement omnicanal "
        "Try-On virtuel + moteur IA de recommandation vestimentaire. "
        "Contrat-cadre 24 mois incluant : intégration API, maintenance, "
        "formation équipes, support prioritaire."
    ),
    "importe_ht_eur": 967_244.67,
    "tva_pct": 20.0,
    "tva_eur": 193_448.93,
    "importe_ttc_eur": 1_160_693.60,
    "devise": "EUR",
    "duree_mois": 24,
    "date_emission": "2026-04-21",
    "date_echeance": "2028-04-21",
    "statut": "EMISE",
    "reference_patente": PATENTE,
    "beneficiaire": ENTITY,
    "beneficiaire_siren": SIREN,
    "beneficiaire_siret": SIRET,
    "iban": IBAN,
    "bic": BIC,
}


def _nivel_1_total() -> float:
    """Total de la tesorería operativa (Nivel 1)."""
    nodos_activos = NODO_LVMH + NODO_WESTFIELD
    transferencia_ip = TRANSFERENCIA_IP_UNIT * 2
    return round(
        ATRASOS_PILOTO + nodos_activos + transferencia_ip + SUBVENCION_BFT, 2
    )


def _nivel_2_total() -> float:
    """Total del contrato marco (Nivel 2)."""
    return FACTURA_F_2026_001["importe_ttc_eur"]


def master_ledger() -> dict:
    """
    Master Ledger consolidado con los dos niveles de facturación.

    Nivel 1: Tesorería operativa de proyectos a corto plazo.
    Nivel 2: Contrato marco F-2026-001 a 24 meses.
    """
    n1 = _nivel_1_total()
    n2 = _nivel_2_total()
    return {
        "entity": ENTITY,
        "siren": SIREN,
        "siret": SIRET,
        "patente": PATENTE,
        "iban": IBAN,
        "bic": BIC,
        "ts": datetime.now(timezone.utc).isoformat(),
        "nivel_1_tesoreria_operativa": {
            "descripcion": "Tesorería de proyectos operativos a corto plazo",
            "conceptos": {
                "atrasos_piloto_eur": ATRASOS_PILOTO,
                "nodo_lvmh_eur": NODO_LVMH,
                "nodo_westfield_eur": NODO_WESTFIELD,
                "transferencia_ip_eur": TRANSFERENCIA_IP_UNIT * 2,
                "subvencion_bpifrance_eur": SUBVENCION_BFT,
            },
            "total_eur": n1,
            "bpifrance": BPIFRANCE_LEDGER,
        },
        "nivel_2_contrato_marco": {
            "descripcion": "Contrat-cadre 24 mois — Galeries Lafayette Haussmann",
            "factura": FACTURA_F_2026_001,
            "total_ttc_eur": n2,
        },
        "capital_total_consolidado_eur": round(n1 + n2, 2),
        "SOUVERAINETÉ": 1,
    }


def ledger_soberano() -> dict[str, object]:
    """
    Devuelve el ledger soberano actualizado para el frente Bpifrance.
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
    Calcula el capital total reclamado en el pipeline de cobro soberano V12.
    """
    nodos_activos = NODO_LVMH + NODO_WESTFIELD
    transferencia_ip = TRANSFERENCIA_IP_UNIT * 2
    total = ATRASOS_PILOTO + nodos_activos + transferencia_ip + SUBVENCION_BFT

    print("--- [ESTADO FINANCIERO TOTAL: TRYONYOU V12] ---")
    print(f"CAPITAL TOTAL RECLAMADO: {total:,.2f} €")
    print(
        "ESTADO: Pipeline de cobro al 100% de capacidad. "
        f"BPIFRANCE en {BPIFRANCE_LEDGER['estado_actual']}."
    )
    return total
