
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import hashlib
import sys
from pathlib import Path

_api_dir = Path(__file__).resolve().parent
if str(_api_dir) not in sys.path:
    sys.path.insert(0, str(_api_dir))

from shopify_bridge import resolve_shopify_checkout_url
from stripe_connect import router as stripe_connect_router

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

# Stripe Connect seller dashboard routes
app.include_router(stripe_connect_router, prefix="/api")

# Modelos de datos
class SelectionRequest(BaseModel):
    garment_id: str
    size: str
    user_id: str

# Rutas principales del piloto
@app.get("/")
async def root():
    return {"status": "online", "message": "TryOnYou API Funcionando"}

@app.post("/api/select-perfect")
async def select_perfect(request: SelectionRequest):
    """Añade la prenda al carrito con la talla correcta."""
    try:
        # Lógica para procesar la selección
        return {
            "success": True, 
            "message": f"Prenda {request.garment_id} añadida en talla {request.size}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/combinations/{user_id}")
async def get_combinations(user_id: str):
    """Devuelve las 5 sugerencias de prendas del algoritmo."""
    # Simulación de respuesta del algoritmo de escaneo
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


@app.post("/api/v1/checkout/perfect-selection")
async def perfect_checkout_selection(data: dict):
    """Checkout de certeza — vincula hash biométrico (_Sovereignty_ID) al pedido Shopify (Zero-Size)."""
    biometric_hash = str(data.get("biometric_hash", "")).strip()
    fabric_sensation = str(data.get("fabric_sensation", "")).strip()
    code = str(data.get("code", "")).strip()

    # Identificador de sesión estable derivado del hash biométrico (SHA-256 → 7 dígitos).
    seed = (biometric_hash or fabric_sensation or code or "0").encode("utf-8")
    lead_id = int(hashlib.sha256(seed).hexdigest(), 16) % 10_000_000

    url = resolve_shopify_checkout_url(lead_id, fabric_sensation, biometric_hash)

    result: dict = {}
    if url:
        result["checkout_primary_url"] = url
        result["checkout_shopify_url"] = url
    return result

# Adaptador para Vercel (si es necesario)
# handler = app

