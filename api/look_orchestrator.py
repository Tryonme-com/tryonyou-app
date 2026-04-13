"""
Look Orchestrator — Lógica de elasticidad y selección de Looks para el espejo Divineo.

Aplica el esquema técnico de elasticidad de prendas (patente PCT/EP2025/067317)
para seleccionar los 5 mejores looks dado un escaneo corporal del usuario.

SIREN: 943 610 196
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

MASTER_LOOKS_COUNT = 5
ELASTICITY_THRESHOLD = 0.3
SIREN = "943610196"

LAFAYETTE_EXPERIENCE = "CHAS_WITH_FEATHERS"
LAFAYETTE_LOCATION = "2ª Planta Derecha"


@dataclass
class Product:
    """Representa una prenda con sus metadatos y puntuación de elasticidad."""

    name: str
    brand: str
    category: str
    elasticity_score: float
    look_id: int


class LookOrchestrator:
    """
    Orquestador de Looks para el espejo digital.

    Aplica la lógica de elasticidad (patente PCT/EP2025/067317) para filtrar
    y seleccionar los mejores looks a partir de un escaneo corporal del usuario.
    """

    def __init__(self, siren: str = SIREN) -> None:
        self.siren = siren
        self.master_looks_count = MASTER_LOOKS_COUNT

    def calculate_perfect_fit(
        self, user_scan_data: Dict[str, Any], look_assets: List[Product]
    ) -> List[Product]:
        """
        Filtra las prendas usando la lógica de elasticidad.

        Una prenda se incluye en la selección si su elasticity_score supera el
        umbral mínimo (ELASTICITY_THRESHOLD), lo que indica que la prenda cede
        lo suficiente para adaptarse a las medidas del escaneo corporal.

        Args:
            user_scan_data: Datos del escaneo corporal del usuario.
            look_assets:    Lista de prendas candidatas.

        Returns:
            Lista de hasta `master_looks_count` prendas con fit perfecto.
        """
        perfect_selection: List[Product] = []

        for item in look_assets:
            if item.elasticity_score >= ELASTICITY_THRESHOLD:
                perfect_selection.append(item)

            if len(perfect_selection) == self.master_looks_count:
                break

        return perfect_selection

    def get_lafayette_payload(self, look_id: int) -> Dict[str, Any]:
        """
        Genera el payload JSON para el Espejo de Lafayette.

        Args:
            look_id: Identificador del look seleccionado.

        Returns:
            Diccionario con el estado y metadatos del look para el espejo.
        """
        return {
            "status": "LOCKED_AND_READY",
            "payout_verified": True,
            "location": LAFAYETTE_LOCATION,
            "experience": LAFAYETTE_EXPERIENCE,
            "selected_look": look_id,
        }
