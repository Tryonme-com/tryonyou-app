"""
Supervisor asíncrono — lectura de saldo Stripe vía httpx (clave desde entorno).
"""
import asyncio
import os
from datetime import datetime

import httpx

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in __import__("sys").path:
    __import__("sys").path.insert(0, _ROOT)

from stripe_fr_resolve import resolve_stripe_secret_fr

# CONFIGURACION — nunca claves en código; usar STRIPE_SECRET_KEY_FR u otras resueltas
STRIPE_API_KEY = resolve_stripe_secret_fr()
HEADERS = (
    {"Authorization": f"Bearer {STRIPE_API_KEY}"} if STRIPE_API_KEY else {}
)
BASE_URL = "https://api.stripe.com/v1"

async def check_everything():
    async with httpx.AsyncClient() as client:
        print(f"[{datetime.now()}] Iniciando supervisión del sistema...")
        
        # 1. Verificar Balance (El dinero real)
        balance = await client.get(f"{BASE_URL}/balance", headers=HEADERS)
        
        # 2. Verificar Pagos de Lafayette
        payments = await client.get(f"{BASE_URL}/payment_intents?limit=1", headers=HEADERS)
        
        # PROCESAMIENTO LOGICO
        if balance.status_code == 200:
            data = balance.json()
            available = data.get("available", [])
            print(f"--- ESTADO DEL CAPITAL ---")
            print(f"Fondos disponibles: {available[0]['amount'] / 100} {available[0]['currency'].upper()}")
        
        # 3. Alerta de Seguridad si algo falla
        if balance.status_code != 200:
            print("ERROR CRITICO: Conexion interrumpida con Stripe.")
        else:
            print("SISTEMA OPERATIVO: Todo en orden.")

if __name__ == "__main__":
    asyncio.run(check_everything())
    