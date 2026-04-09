"""
Mirror Overlay Engine V10:
- Selecciona prenda desde inventario (base de datos JSON)
- Compara contra medidas estimadas del cliente
- Pasa por Robert Engine para fit report
- Devuelve payload listo para overlay sobre gemelo digital

Patente: PCT/EP2025/067317
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from inventory_engine import inventory_match_payload
from robert_engine import RobertEngine

PATENTE = "PCT/EP2025/067317"
_ROOT = Path(__file__).resolve().parent.parent
_INVENTORY_JSON = _ROOT / "current_inventory.json"

_BRAND_COLORS = {
    "BALMAIN": "#e5e0d3",
    "ARMARIO SOLIDARIO": "#9fc5e8",
    "ARMARIO INTELIGENTE": "#c4dfb7",
    "SAC MUSEUM": "#f4cccc",
}

_BRAND_IMAGE_FALLBACK = {
    "BALMAIN": "https://images.unsplash.com/photo-1594938298603-c8148c4b4057?w=900&q=80",
    "ARMARIO SOLIDARIO": "https://images.unsplash.com/photo-1529139574466-a303027c1d8b?w=900&q=80",
    "ARMARIO INTELIGENTE": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=900&q=80",
    "SAC MUSEUM": "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=900&q=80",
}


def _safe_float(v: Any, default: float) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _load_inventory_rows() -> list[dict[str, Any]]:
    if not _INVENTORY_JSON.is_file():
        return []
    try:
        data = json.loads(_INVENTORY_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(data, list):
        return []
    out: list[dict[str, Any]] = []
    for row in data:
        if isinstance(row, dict) and row.get("id"):
            out.append(row)
    return out


def _inventory_distance_score(row: dict[str, Any], shoulder_est: float, waist_est: float) -> float:
    tech = row.get("technical_specs", {}) if isinstance(row.get("technical_specs"), dict) else {}
    shoulder_max = _safe_float(tech.get("shoulder_max"), 44.0)
    waist_max = _safe_float(tech.get("waist_max"), 32.0)
    ds = abs(shoulder_est - shoulder_max) / max(shoulder_max, 1.0)
    dw = abs(waist_est - waist_max) / max(waist_max, 1.0)
    stock_bonus = 0.0 if bool(row.get("stock_status", True)) else 0.25
    return ds + dw + stock_bonus


def _normalize_img(raw: str, brand: str) -> str:
    x = (raw or "").strip()
    if not x:
        return _BRAND_IMAGE_FALLBACK.get(brand.upper(), _BRAND_IMAGE_FALLBACK["BALMAIN"])
    if x.startswith("http://") or x.startswith("https://") or x.startswith("/"):
        return x
    return "/" + x.lstrip("./")


def _pick_best_garment(shoulder_est: float, waist_est: float) -> dict[str, Any]:
    rows = _load_inventory_rows()
    if not rows:
        return {
            "id": "V10-BALMAIN-WHITE-SNAP",
            "brand": "BALMAIN",
            "name": "Silhouette pilote blanche — Lafayette",
            "img": _BRAND_IMAGE_FALLBACK["BALMAIN"],
            "stock_status": True,
            "technical_specs": {"shoulder_max": 44, "waist_max": 32},
        }
    best = min(rows, key=lambda row: _inventory_distance_score(row, shoulder_est, waist_est))
    return best


def build_mirror_overlay_payload(body: dict[str, Any]) -> tuple[dict[str, Any], int]:
    """
    Payload principal para overlay de prenda sobre gemelo digital.

    body esperado (todo opcional):
      - shoulder_w_px, hip_y_px
      - shoulder_est, waist_est (escala pseudo-cm derivada de landmarks)
      - frame_spec: {w, h}
      - fabric_fit_verdict / fabric_sensation
    """
    frame_spec = body.get("frame_spec", {}) if isinstance(body.get("frame_spec"), dict) else {}
    frame_w = int(_safe_float(frame_spec.get("w"), 1080))
    frame_h = int(_safe_float(frame_spec.get("h"), 1920))

    shoulder_w_px = _safe_float(body.get("shoulder_w_px"), frame_w * 0.22)
    hip_y_px = _safe_float(body.get("hip_y_px"), frame_h * 0.56)
    fit_seed = _safe_float(body.get("fit_score_seed"), 92.0)

    shoulder_est = _safe_float(body.get("shoulder_est"), 44.0)
    waist_est = _safe_float(body.get("waist_est"), 32.0)

    garment = _pick_best_garment(shoulder_est, waist_est)
    brand = str(garment.get("brand", "BALMAIN")).strip() or "BALMAIN"
    color = _BRAND_COLORS.get(brand.upper(), "#d4af37")
    image_url = _normalize_img(str(garment.get("img", "")), brand)

    fit_report = RobertEngine().process_frame(
        fabric_key=str(garment.get("id", "V10-BALMAIN-WHITE-SNAP")),
        shoulder_w=shoulder_w_px,
        hip_y=hip_y_px,
        fit_score=fit_seed,
        frame_spec={"w": frame_w, "h": frame_h},
    )

    inv_match = inventory_match_payload(
        {
            "fabric_sensation": body.get("fabric_sensation", ""),
            "fabric_fit_verdict": body.get("fabric_fit_verdict", ""),
            "snap": True,
        }
    )

    confidence = max(
        0.0,
        min(1.0, 1.0 - _inventory_distance_score(garment, shoulder_est, waist_est)),
    )

    return {
        "status": "ok",
        "protocol": "zero_size",
        "patente": PATENTE,
        "selected_garment": {
            "id": str(garment.get("id", "V10-BALMAIN-WHITE-SNAP")),
            "brand": brand,
            "name": str(garment.get("name", "Silueta seleccionada")),
            "image_url": image_url,
            "color_hex": color,
            "confidence": round(confidence, 4),
        },
        "fit_report": fit_report,
        "inventory_match": inv_match,
        "overlay_hint": {
            "mode": "torso_trapezoid",
            "alpha": 0.54,
            "top_offset_ratio": -0.06,
            "bottom_extension_ratio": 0.22,
        },
    }, 200
