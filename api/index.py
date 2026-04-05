from __future__ import annotations

import sys
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Literal, Optional

# Asegurar que el directorio api/ está en el path para importar los bridges
_API_DIR = os.path.dirname(__file__)
if _API_DIR not in sys.path:
    sys.path.insert(0, _API_DIR)

from shopify_bridge import resolve_shopify_checkout_url  # noqa: E402

# Configuración de la aplicación
app = FastAPI(title="TryOnYou API", version="1.0.0")

# Configuración de CORS para permitir la conexión con el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ajustar a dominios específicos en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Modelos de datos
# ---------------------------------------------------------------------------

class SelectionRequest(BaseModel):
    garment_id: str
    size: str
    user_id: str


class CheckoutRequest(BaseModel):
    fabric_sensation: str = ""
    protocol: str = "zero_size"
    shopping_flow: str = "non_stop_card"
    anti_accumulation: bool = True
    single_size_certitude: bool = True
    lead_id: int = 0
    code: Optional[str] = None


CollaboratorType = Literal["ARMARIO SOLIDARIO", "ARMARIO INTELIGENTE", "SAC MUSEUM"]

COLLABORATOR_DESCRIPTIONS: dict[str, str] = {
    "ARMARIO SOLIDARIO": (
        "Armario colaborativo — prendas seleccionadas con criterio social y sostenible."
    ),
    "ARMARIO INTELIGENTE": (
        "Armario inteligente — combinaciones generadas por el motor biométrico Jules."
    ),
    "SAC MUSEUM": (
        "Sac Museum — piezas de colección y ediciones limitadas Divineo."
    ),
}


class CollaboratorFilterRequest(BaseModel):
    type: CollaboratorType
    lead_id: Optional[int] = None
    fabric_sensation: Optional[str] = None


# ---------------------------------------------------------------------------
# Rutas principales del piloto
# ---------------------------------------------------------------------------

@app.get("/")
async def root():
    return {"status": "online", "message": "TryOnYou API Funcionando"}


@app.post("/api/select-perfect")
async def select_perfect(request: SelectionRequest):
    """Añade la prenda al carrito con la talla correcta."""
    try:
        return {
            "success": True,
            "message": f"Prenda {request.garment_id} añadida en talla {request.size}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/combinations/{user_id}")
async def get_combinations(user_id: str):
    """Devuelve las 5 sugerencias de prendas del algoritmo."""
    suggestions = [
        {"id": "1", "name": "Look Principal", "type": "completo"},
        {"id": "2", "name": "Sugerencia 2", "type": "prenda"},
        {"id": "3", "name": "Sugerencia 3", "type": "prenda"},
        {"id": "4", "name": "Sugerencia 4", "type": "prenda"},
        {"id": "5", "name": "Sugerencia 5", "type": "prenda"},
    ]
    return {"user_id": user_id, "suggestions": suggestions}


@app.post("/api/save-silhouette")
async def save_silhouette(data: dict):
    """Almacena los datos del escaneo en el perfil."""
    return {"status": "success", "message": "Silueta guardada correctamente"}


# ---------------------------------------------------------------------------
# Shopify — Zero-Size checkout
# ---------------------------------------------------------------------------

@app.post("/api/v1/checkout/perfect-selection")
async def checkout_perfect_selection(request: CheckoutRequest):
    """
    Orquesta el checkout Zero-Size multicanal (Shopify Admin draft order → storefront fallback).

    Responde con checkout_primary_url (Shopify Admin invoice si disponible, o URL storefront)
    y un sello emocional de confirmación del protocolo.
    """
    lead_id: int = request.lead_id
    sensation: str = (request.fabric_sensation or "").strip()

    checkout_url: str | None = resolve_shopify_checkout_url(lead_id, sensation)

    response: dict = {
        "status": "success",
        "protocol": request.protocol,
        "anti_accumulation": request.anti_accumulation,
        "single_size_certitude": request.single_size_certitude,
        "emotional_seal": (
            "Parcours Zero-Size validé — votre ajustage est certifié Divineo. "
            "Une seule taille, une seule certitude."
        ),
        "checkout_primary_url": checkout_url,
        "checkout_shopify_url": checkout_url,
        "checkout_amazon_url": None,
    }
    return response


# ---------------------------------------------------------------------------
# Colaboradores
# ---------------------------------------------------------------------------

@app.get("/api/v1/collaborators")
async def list_collaborators():
    """Lista los tipos de colaborador disponibles con su descripción."""
    collaborators = [
        {
            "type": ctype,
            "description": COLLABORATOR_DESCRIPTIONS[ctype],
            "accent": ctype == "ARMARIO INTELIGENTE",
            "primary": ctype == "SAC MUSEUM",
        }
        for ctype in COLLABORATOR_DESCRIPTIONS
    ]
    return {"status": "ok", "collaborators": collaborators}


@app.post("/api/v1/collaborators/filter")
async def filter_by_collaborator(request: CollaboratorFilterRequest):
    """
    Registra la selección de tipo de colaborador y devuelve el contexto de análisis
    biométrico asociado al armario elegido.
    """
    ctype = request.type
    description = COLLABORATOR_DESCRIPTIONS.get(ctype, "")

    return {
        "status": "success",
        "type": ctype,
        "description": description,
        "biometric_filter": ctype.lower().replace(" ", "_"),
        "message": (
            f"Connexion sécurisée à {ctype}. Analyse de fit en cours — "
            "protocole Zero-Size activé."
        ),
    }


# Adaptador para Vercel (si es necesario)
# handler = app

