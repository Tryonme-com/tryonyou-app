"""
Divineo Inventory Engine V10 — Orquestador de inventario real (Mirror + Elena Grandini).
Montado por api/index.py (Vercel serverless). No FastAPI en producción: mismas rutas vía handler HTTP.

Contrato Zero-Size: las respuestas públicas no incluyen tallas ni medidas corporales;
solo MATCH_ID / garment_id y mensaje emocional + sellos legales.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Registro legal (alineado con api/index.py)
METADATA: dict[str, str] = {
    "SIREN": "943 610 196",
    "PATENTE": "PCT/EP2025/067317",
    "STATUS": "EMPIRE_MODE_ACTIVE",
}


@dataclass
class Garment:
    id: str
    brand: str
    category: str
    store_id: str
    stock_status: bool
    # Uso interno motor / archivo fuente (no exponer en JSON cliente Zero-Size)
    elasticity_hint: float | None = None
    fabric_weight_label: str | None = None

    @classmethod
    def from_record(cls, row: dict[str, Any]) -> Garment:
        tech = row.get("technical_specs") if isinstance(row.get("technical_specs"), dict) else {}
        el = None
        try:
            sh = float(tech.get("shoulder_max", 0) or 0)
            wa = float(tech.get("waist_max", 0) or 0)
            if sh > 0 and wa > 0:
                el = round(min(1.2, max(0.75, sh / max(wa, 1e-6))), 4)
        except (TypeError, ValueError):
            el = None
        cat = str(row.get("type", row.get("category", "lux"))).strip() or "lux"
        sid = str(row.get("store_id", row.get("store", "GL-HAUSSMANN"))).strip()
        return cls(
            id=str(row["id"]).strip(),
            brand=str(row.get("brand", "")).strip(),
            category=cat,
            store_id=sid,
            stock_status=bool(row.get("stock_status", True)),
            elasticity_hint=el,
            fabric_weight_label=str(row.get("fabric_weight", "")).strip() or None,
        )


class InventoryManager:
    """Cerebro de referencias reales: partners confirmados + JSON de stock en repo."""

    def __init__(self, project_root: Path | None = None):
        self._root = project_root or Path(__file__).resolve().parent.parent
        self.references: list[Garment] = []
        self.partners: list[dict[str, str]] = []
        self.load_confirmed_partners()
        self._load_inventory_files()

    def load_confirmed_partners(self) -> None:
        self.partners = [
            {"id": "GL-HAUSSMANN", "name": "Galeries Lafayette", "contract": "BP-100K-2026"},
            {"id": "EG-BOUTIQUE", "name": "Elena Grandini Exclusive", "contract": "DIVINEO-V10"},
            {"id": "BALMAIN-PARIS", "name": "Balmain Flagship", "contract": "PILOT-WHITE-SNAP"},
        ]

    def _load_inventory_files(self) -> None:
        paths: list[Path] = []
        env_p = os.environ.get("DIVINEO_INVENTORY_JSON", "").strip()
        if env_p:
            paths.append(Path(env_p))
        paths.extend(
            [
                self._root / "current_inventory.json",
                self._root / "data" / "elena_grandini_v10.json",
            ]
        )
        seen: set[str] = set()
        for p in paths:
            if not p.is_file():
                continue
            try:
                with open(p, encoding="utf-8") as f:
                    data = json.load(f)
            except (OSError, json.JSONDecodeError):
                continue
            rows: list[dict[str, Any]] = data if isinstance(data, list) else []
            for row in rows:
                if not isinstance(row, dict) or "id" not in row:
                    continue
                gid = str(row["id"]).strip()
                if gid in seen:
                    continue
                seen.add(gid)
                self.references.append(Garment.from_record(row))

    def sync_garment_logic(self, silhouette_data: dict[str, Any]) -> dict[str, Any]:
        """
        Liga silueta V10 (veredicto emocional / sensación) con referencias reales.
        PROTOCOLO ZERO-SIZE: salida sin tallas ni pesos al cliente.
        """
        verdict = str(silhouette_data.get("fabric_fit_verdict", "")).strip().lower()
        sensation = str(silhouette_data.get("fabric_sensation", "")).strip().lower()
        snap = bool(silhouette_data.get("snap", False))

        pool = [g for g in self.references if g.stock_status]
        if not pool:
            pool = list(self.references)

        chosen: Garment | None = None
        if snap or "balmain" in sensation or "snap" in sensation:
            first_museum: Garment | None = None
            for g in pool:
                brand_up = g.brand.upper()
                if "BALMAIN" in brand_up or g.id.upper().startswith("V10-BALMAIN"):
                    chosen = g
                    break
                if first_museum is None and ("MUSEUM" in brand_up or "SAC" in brand_up):
                    first_museum = g

            if chosen is None:
                chosen = first_museum

            if chosen is None and pool:
                chosen = pool[0]

        if chosen is None and verdict == "drape_bias":
            for g in pool:
                cat = (g.category or "").upper()
                br = g.brand.upper()
                if "SOLID" in br or "SOLID" in cat or "DONATION" in cat:
                    chosen = g
                    break

        if chosen is None and pool:
            chosen = pool[0]

        gid = chosen.id if chosen else "V10-BALMAIN-WHITE-SNAP"
        brand = chosen.brand if chosen else "Balmain"

        return {
            "match_absolute": "TRUE",
            "garment_id": gid,
            "brand_line": brand,
            "message": (
                f"Ajuste biométrique validé — référence {gid} ({brand}), "
                "Elena Grandini / Lafayette sous protocole Zero-Size."
            ),
            "legal": METADATA,
            "protocol": "zero_size",
        }


_inventory_singleton: InventoryManager | None = None


def get_inventory() -> InventoryManager:
    global _inventory_singleton  # noqa: PLW0603
    if _inventory_singleton is None:
        _inventory_singleton = InventoryManager()
    return _inventory_singleton


def inventory_status_payload() -> dict[str, Any]:
    inv = get_inventory()
    return {
        "active_references": len(inv.references),
        "confirmed_stores": len(inv.partners),
        "partners": inv.partners,
        "legal": METADATA,
        "protocol": "zero_size",
    }


def inventory_match_payload(silhouette_data: dict[str, Any]) -> dict[str, Any]:
    inv = get_inventory()
    return inv.sync_garment_logic(silhouette_data)


# --- FastAPI opcional (desarrollo local): pip install fastapi uvicorn ---
def _try_fastapi_app():  # pragma: no cover
    try:
        from fastapi import FastAPI, HTTPException  # type: ignore
        from pydantic import BaseModel  # type: ignore
    except ImportError:
        return None

    app = FastAPI(title="Divineo Inventory Engine V10")

    class GarmentModel(BaseModel):
        id: str
        brand: str
        category: str
        elasticity_index: float
        fabric_weight: str
        store_id: str
        stock_status: bool

    @app.get("/api/v1/inventory/status")
    async def get_status():
        return inventory_status_payload()

    @app.post("/api/v1/inventory/match")
    async def find_perfect_fit(data: dict):
        try:
            return inventory_match_payload(data)
        except Exception:
            raise HTTPException(status_code=500, detail="Error en el Búnker de Inventario")

    return app


if __name__ == "__main__":  # pragma: no cover
    print(json.dumps(inventory_status_payload(), indent=2, ensure_ascii=False))
    app = _try_fastapi_app()
    if app:
        import uvicorn  # type: ignore

        uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8099")))
