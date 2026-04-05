
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import hashlib
import os
import sys
from pathlib import Path

_api_dir = Path(__file__).resolve().parent
_root_dir = _api_dir.parent
for _p in (_api_dir, _root_dir):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from shopify_bridge import resolve_shopify_checkout_url
from stripe_connect_manager import (
    TryOnYouManager,
    TryOnYouOrchestrator,
    WEBHOOK_SECRET,
    stripe_client,
)

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

# ---------------------------------------------------------------------------
# Stripe Connect — Plataforma de pagos
# ---------------------------------------------------------------------------

_stripe_manager = TryOnYouManager()


class ConnectAccountRequest(BaseModel):
    email: str
    name: str


class OnboardingLinkRequest(BaseModel):
    account_id: str
    return_url: str


class CheckoutRequest(BaseModel):
    price_id: str
    destination_account: str
    success_url: Optional[str] = "https://tryonyou.com/success"
    cancel_url: Optional[str] = None


@app.post("/api/stripe/connect/create-account")
async def stripe_create_account(req: ConnectAccountRequest):
    """Crea una cuenta Stripe Connect V2 para un vendedor."""
    try:
        account_id = _stripe_manager.create_connected_account(req.email, req.name)
        return {"success": True, "account_id": account_id}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/stripe/connect/onboarding-link")
async def stripe_onboarding_link(req: OnboardingLinkRequest):
    """Genera un link de onboarding para completar la verificación del vendedor."""
    try:
        url = _stripe_manager.get_onboarding_link(req.account_id, req.return_url)
        return {"success": True, "url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stripe/connect/account-status/{account_id}")
async def stripe_account_status(account_id: str):
    """Verifica el estado de una cuenta Connect (transferencias activas, onboarding)."""
    try:
        status = _stripe_manager.check_account_status(account_id)
        return {"success": True, **status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/stripe/checkout/create-session")
async def stripe_create_checkout(req: CheckoutRequest):
    """Crea una Checkout Session con Destination Charge y comisión de plataforma."""
    try:
        url = _stripe_manager.create_checkout_session(
            price_id=req.price_id,
            destination_account=req.destination_account,
            success_url=req.success_url or "https://tryonyou.com/success",
            cancel_url=req.cancel_url,
        )
        return {"success": True, "checkout_url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/stripe/webhook")
async def stripe_webhook(request: Request):
    """Recibe eventos de Stripe (webhooks) y procesa los relevantes."""
    import stripe as _stripe

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    if not WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="Webhook secret not configured")

    try:
        event = _stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
    except _stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    event_type = event.get("type", "")

    if event_type == "checkout.session.completed":
        session = event["data"]["object"]
        return JSONResponse(
            {"received": True, "type": event_type, "session_id": session.get("id")}
        )

    if event_type == "account.updated":
        account = event["data"]["object"]
        return JSONResponse(
            {"received": True, "type": event_type, "account_id": account.get("id")}
        )

    return JSONResponse({"received": True, "type": event_type})


# ---------------------------------------------------------------------------
# Orchestrator — Lafayette + Bpifrance
# ---------------------------------------------------------------------------

_orchestrator = TryOnYouOrchestrator()


class LafayetteCheckoutRequest(BaseModel):
    destination_account: str
    success_url: Optional[str] = "https://tryonyou.com/success"
    cancel_url: Optional[str] = None


@app.get("/api/stripe/bpifrance/solvency-report")
async def bpifrance_solvency_report():
    """Genera el reporte de solvencia para Bpifrance vinculado a activos y contrato Lafayette."""
    return {"success": True, "report": _orchestrator.generate_bpi_report()}


@app.post("/api/stripe/lafayette/checkout")
async def lafayette_checkout(req: LafayetteCheckoutRequest):
    """Crea Checkout Session para el cobro Pack Empire Lafayette con Destination Charge + comisión 5 %."""
    try:
        url = _orchestrator.create_lafayette_checkout(
            destination_account=req.destination_account,
            success_url=req.success_url or "https://tryonyou.com/success",
            cancel_url=req.cancel_url,
        )
        report = _orchestrator.generate_bpi_report()
        return {"success": True, "checkout_url": url, "solvency_report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class V2EventRequest(BaseModel):
    event_id: str


@app.post("/api/stripe/v2/process-event")
async def process_v2_event(req: V2EventRequest):
    """Recupera y procesa un Thin Event de la API V2 de Stripe."""
    try:
        result = TryOnYouOrchestrator.handle_v2_thin_event(req.event_id)
        return {"success": True, **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Adaptador para Vercel (si es necesario)
# handler = app

