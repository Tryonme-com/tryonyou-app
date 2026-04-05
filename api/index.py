
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

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

# Adaptador para Vercel (si es necesario)
# handler = app

