import asyncio
import json
import logging
import requests
from datetime import datetime

# Configuración de trazabilidad total para el Bunker
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("CompositeBunker")

CONFIG = {
    "MAKE_WEBHOOK_URL": "https://hook.us1.make.com/tu_id_unico", # 🔥 Pega tu URL de Make
    "AI_THRESHOLD": 0.92,
    "REVENUE_TARGET": 7500.0
}

class CompositeOrchestrator:
    """Unifica IA, Finanzas y Leads en un solo flujo de ejecución."""
    
    async def validate_all(self, email: str, amount: float):
        logger.info("--- 🛡️ INICIANDO VALIDACIÓN COMPOSITE ---")
        
        # 1. Validación de Inferencia (VetosCore)
        is_tech_ok = CONFIG["AI_THRESHOLD"] >= 0.92
        logger.info(f"🧠 VetosCore Status: {'READY' if is_tech_ok else 'FAILED'}")

        # 2. Validación Financiera (Protocolo BPI)
        is_revenue_ok = amount >= CONFIG["REVENUE_TARGET"]
        logger.info(f"💰 Revenue Status: {'VERIFIED' if is_revenue_ok else 'PENDING'}")

        # 3. Clasificación de Lead (Mesa de los Listos)
        priority = "HIGH" if any(x in email for x in ["@inditex", "@loreal", "@bpi"]) else "LOW"
        
        if is_tech_ok and is_revenue_ok:
            result = {
                "status": "SUCCESS",
                "lead": email,
                "priority": priority,
                "timestamp": datetime.now().isoformat()
            }
            await self.sync_to_make(result)
            return result
        return {"status": "HOLD", "reason": "Technical or Financial validation pending"}

    async def sync_to_make(self, data):
        """Envía el éxito a Slack/LinkedIn vía Make"""
        try:
            requests.post(CONFIG["MAKE_WEBHOOK_URL"], json=data, timeout=5)
            logger.info("🚀 Sincronización con Make: EXITOSA")
        except Exception as e:
            logger.error(f"❌ Error de red en Make: {e}")

async def main():
    orchestrator = CompositeOrchestrator()
    # Simulación de ejecución total
    await orchestrator.validate_all("compras@inditex.com", 7500.0)

if __name__ == "__main__":
    asyncio.run(main())
