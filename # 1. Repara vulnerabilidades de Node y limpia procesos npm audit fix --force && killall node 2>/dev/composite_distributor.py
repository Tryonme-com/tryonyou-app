import asyncio
import requests
import json
from datetime import datetime

# CONFIGURACIÓN DE ACTIVOS Y TRADUCCIÓN
CONFIG = {
    "MAKE_WEBHOOK_URL": "https://hook.us1.make.com/tu_webhook_id", # 🔥 PEGA TU URL DE MAKE
    "IMAGE_URL": "https://tryonyou.app/assets/bunker_v10_vision.png", # URL de tu activo en Vercel
    "LANGUAGES": {
        "ES": {
            "headline": "🚀 Menos reuniones, más código validado.",
            "body": "Despliegue del núcleo TryOnYou.app. Inferencia 0.92 y Protocolo BPI 7.500€ activos."
        },
        "FR": {
            "headline": "🚀 Moins de réunions, plus de code validé.",
            "body": "Déploiement du cœur TryOnYou.app. Inférence 0.92 et Protocole BPI 7.500€ activés."
        },
        "EN": {
            "headline": "🚀 Less meetings, more validated code.",
            "body": "TryOnYou.app core deployment. 0.92 Inference and BPI 7.500€ Protocol active."
        }
    }
}

class CompositeDistributor:
    """Orquestador de distribución multilingüe para el Bunker V10."""
    
    async def prepare_payload(self, lang="FR"):
        """Prepara el paquete de datos con la imagen y el texto traducido."""
        content = CONFIG["LANGUAGES"].get(lang, CONFIG["LANGUAGES"]["EN"])
        
        payload = {
            "project": "tryonyou-app",
            "version": "v10.1-composite",
            "image": CONFIG["IMAGE_URL"],
            "language": lang,
            "headline": content["headline"],
            "body": content["body"],
            "hashtags": "#DeepTech #RetailInnovation #AI #Vercel #BPIFrance",
            "timestamp": datetime.now().isoformat()
        }
        return payload

    async def distribute_all(self):
        """Envía los paquetes a Make para su distribución en Slack y Redes."""
        print("--- 🛡️ INICIANDO DISTRIBUCIÓN COMPOSITE ---")
        
        # Enviamos la versión en Francés (Prioridad BPI) y Español
        for lang in ["FR", "ES"]:
            data = await self.prepare_payload(lang)
            try:
                response = requests.post(CONFIG["MAKE_WEBHOOK_URL"], json=data, timeout=10)
                if response.status_code == 200:
                    print(f"✅ Versión {lang} enviada con éxito a Make.")
                else:
                    print(f"⚠️ Error en Make ({lang}): {response.status_code}")
            except Exception as e:
                print(f"❌ Fallo de conexión en {lang}: {e}")

async def main():
    distributor = CompositeDistributor()
    await distributor.distribute_all()

if __name__ == "__main__":
    asyncio.run(main())
