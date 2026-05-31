import uuid
import csv
from io import BytesIO
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from typing import List, Dict
import qrcode

app = FastAPI(
    title="TRYONYOU - Sistema Central OMEGA V10.2",
    description="Servidor maestro unificado con catálogo extendido de marcas Lafayette"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DIR_DATA = Path("./data")
DIR_ASSETS = Path("./assets")
DIR_DATA.mkdir(exist_ok=True)
DIR_ASSETS.mkdir(exist_ok=True)

ARCHIVO_INVITADOS_MUSEUM = DIR_DATA / "lista_invitados_sac_museum.csv"

if not ARCHIVO_INVITADOS_MUSEUM.exists():
    with open(ARCHIVO_INVITADOS_MUSEUM, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Fecha_Registro", "Email", "Origen_Captacion", "Estado_Invitacion"])

app.mount("/assets", StaticFiles(directory="assets"), name="assets")

class DatosSilueta(BaseModel):
    puntos_biometricos: List[float]
    proporciones: Dict[str, float]

class PrendaSeleccionada(BaseModel):
    garment_id: str
    talla_calculada: str

class PerfilVIP(BaseModel):
    client_token: str

class RegistroInvitadoVIP(BaseModel):
    email: EmailStr
    origen: str = "Espejo Digital - Efecto Paloma (Lafayette Haussmann)"

CATALOGO_GLOBAL = {
    "balmain": [
        {"id": "blm_01", "nombre": "Blazer Cruzado Estructurado Pierre", "asset": "/assets/balmain_blazer.png", "planta": "Planta 1 - Córner Lujo"},
        {"id": "blm_02", "nombre": "Vestido Knit Monograma Geométrico", "asset": "/assets/balmain_dress.png", "planta": "Planta 1 - Córner Lujo"},
        {"id": "blm_03", "nombre": "Chaqueta Tweed Botones de Oro Vintage", "asset": "/assets/balmain_tweed.png", "planta": "Planta 1 - Córner Lujo"},
        {"id": "blm_04", "nombre": "Top Corsé de Neopreno Satinado", "asset": "/assets/balmain_corset.png", "planta": "Planta 1 - Córner Lujo"},
        {"id": "blm_05", "nombre": "Abrigo Largo Masculino de Lana Negra", "asset": "/assets/balmain_coat.png", "planta": "Planta 1 - Córner Lujo"}
    ],
    "prada": [
        {"id": "prd_01", "nombre": "Abrigo Re-Nylon Minimalista Anthracite", "asset": "/assets/prada_coat.png", "planta": "Planta 2 - Créateurs"},
        {"id": "prd_02", "nombre": "Falda Plisada de Sarga Estructurada", "asset": "/assets/prada_skirt.png", "planta": "Planta 2 - Créateurs"},
        {"id": "prd_03", "nombre": "Traje Técnico Gabardina de Corte Sastre", "asset": "/assets/prada_suit.png", "planta": "Planta 2 - Créateurs"},
        {"id": "prd_04", "nombre": "Chaqueta Corta de Cuero Gastado Umber", "asset": "/assets/prada_leather.png", "planta": "Planta 2 - Créateurs"},
        {"id": "prd_05", "nombre": "Vestido Popelín con Escote Geométrico", "asset": "/assets/prada_dress.png", "planta": "Planta 2 - Créateurs"}
    ],
    "hermes": [
        {"id": "rms_01", "nombre": "Capa Corta en Cachemira Bone Hermès", "asset": "/assets/hermes_cape.png", "planta": "Planta 1 - Córner Lujo"},
        {"id": "rms_02", "nombre": "Pañuelo de Seda Estampado Art Deco", "asset": "/assets/hermes_scarf.png", "planta": "Planta 1 - Córner Lujo"},
        {"id": "rms_03", "nombre": "Chaqueta de Piel Flexible Suave Ecuestre", "asset": "/assets/hermes_leather.png", "planta": "Planta 1 - Córner Lujo"},
        {"id": "rms_04", "nombre": "Jersey Cuello Alto Hilo Trenzado Lino", "asset": "/assets/hermes_knit.png", "planta": "Planta 1 - Córner Lujo"},
        {"id": "rms_05", "nombre": "Pantalón Recto de Lana de Sastrería", "asset": "/assets/hermes_pants.png", "planta": "Planta 1 - Córner Lujo"}
    ]
}

@app.get("/status")
async def get_status():
    return {"status": "online", "engine": "OMEGA_V10.2", "mode": "Empire"}

@app.post("/api/lafayette/carrito")
async def añadir_al_carrito(prenda: PrendaSeleccionada):
    return {"status": "success", "tienda": "Galeries Lafayette Haussmann", "talla_asegurada": prenda.talla_calculada, "filtro": "Zero-Size Active"}

@app.get("/api/lafayette/reservar/{garment_id}")
async def reservar_en_probador(garment_id: str):
    reserva_id = f"GL-{str(uuid.uuid4())[:6].upper()}"
    datos_qr = f"https://tryonyou.lafayette.demo/verify/{reserva_id}"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(datos_qr)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1a1a1a", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return Response(content=buffer.getvalue(), media_type="image/png")

@app.get("/api/lafayette/coleccion/{marca}")
async def obtener_coleccion(marca: str):
    marca_key = marca.lower().strip()
    if marca_key not in CATALOGO_GLOBAL:
        raise HTTPException(status_code=404, detail="Firma no disponible")
    return {"marca": marca, "sugerencias": CATALOGO_GLOBAL[marca_key]}

@app.post("/api/lafayette/silueta/guardar")
async def guardar_silueta(data: DatosSilueta):
    return {"status": "stored", "cliente_referencia": f"LAFAYETTE_USER_{str(uuid.uuid4())[:6].upper()}"}

@app.post("/api/lafayette/metricas")
async def registrar_metricas(metricas: dict):
    print(f"[Métricas] Log guardado: {metricas}")
    return {"status": "recorded"}

@app.post("/api/lafayette/vip/activar")
async def activar_vip(perfil: PerfilVIP):
    return {"status": "EMPIRE_MODE_ACTIVE", "experiencia": "VIP Premium - Efecto Paloma", "probador_privado": "Reservado automáticamente - Salón Haussmann"}

@app.post("/api/lafayette/vip/registrar-museum")
async def registrar_museum(invitado: RegistroInvitadoVIP):
    invitado_existe = False
    if ARCHIVO_INVITADOS_MUSEUM.stat().st_size > 0:
        with open(ARCHIVO_INVITADOS_MUSEUM, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if row and row[1] == invitado.email:
                    invitado_existe = True
                    break
    if invitado_existe:
        return {"status": "already_registered"}
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ARCHIVO_INVITADOS_MUSEUM, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([fecha_actual, invitado.email, invitado.origen, "Pendiente de Envío Entrada"])
    return {"status": "success", "email": invitado.email}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
